from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer
from .scoring import score_tasks
from rest_framework import status

@api_view(['POST'])
def analyze_tasks(request):
    # Expect request.data to be a list of tasks
    tasks = request.data.get('tasks') if isinstance(request.data, dict) else request.data
    strategy = request.query_params.get('strategy', 'smart_balance')
    if not isinstance(tasks, list):
        return Response({"error":"Expecting a JSON list of tasks under root or in 'tasks' key."}, status=status.HTTP_400_BAD_REQUEST)
    # basic validation and normalization
    serializer = TaskSerializer(data=tasks, many=True)
    if not serializer.is_valid():
        return Response({"error":"Invalid task format", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    cleaned = serializer.validated_data
    scored, meta = score_tasks(cleaned, strategy=strategy)
    return Response({"tasks": scored, "meta": meta})

@api_view(['POST', 'GET'])
def suggest_tasks(request):
    # If POST: read tasks from body. If GET: maybe return sample or cached tasks.
    if request.method == 'POST':
        tasks = request.data.get('tasks') if isinstance(request.data, dict) else request.data
    else:
        # for simplicity, require POST list; GET returns 400 unless you have server-side storage
        return Response({"error":"POST a tasks list to get suggestions."}, status=status.HTTP_400_BAD_REQUEST)

    strategy = request.query_params.get('strategy', 'smart_balance')
    serializer = TaskSerializer(data=tasks, many=True)
    if not serializer.is_valid():
        return Response({"error":"Invalid task format", "details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    scored, meta = score_tasks(serializer.validated_data, strategy=strategy)
    top3 = scored[:3]
    # attach explanation for each selected top3
    suggestions = []
    for t in top3:
        suggestions.append({
            "task": t,
            "explanation": f"Selected because: {t.get('reason')}, score {t.get('score')}"
        })
    return Response({"suggestions": suggestions, "meta": meta})
