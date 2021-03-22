from language.models import ForeignLanguage, Translation
from tracking.models import LangySession, LearningTrace
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
import json


def add_learning_traces(request):
    if request.method == 'POST':
        # Get data
        json_data = json.loads(request.body)
        langy_session = get_object_or_404(LangySession, pk=json_data['langy_session_id'])
        translation_ids = json_data['translation_ids']
        mode = json_data['mode']

        # Get user's active ForeignLanguage
        foreign_language = request.user.active_language.foreign_language

        # Convert translation list into a dict of unique IDs and counts
        # This will be used to create new LearningTraces
        translation_ids_counts = {}
        for id in translation_ids:
            if id not in translation_ids_counts.keys():
                # Add new id
                translation_ids_counts[id] = 1
            else:
                # Add to count for this id
                translation_ids_counts[id] += 1

        for id, count in translation_ids_counts.items():
            # Find Translation object
            translation = Translation.objects.filter(id=id).first()
            if translation is None:
                continue  # next Translation


            # Attempt to find existing LearningTrace belonging to this LangySession
            existing = (request.user.traces
                .filter(session = langy_session)
                .filter(translation__foreign_language = foreign_language)
                .filter(translation__id = id)
                .last())
            
            if existing is not None:
                # No need to create a new LearningTrace for this Translation
                # Update appropriate statistic based on tracking mode
                if mode == "seen":              existing.seen += count
                elif mode == "interacted":      existing.interacted += count
                elif mode == "tested":          existing.tested += count
                elif mode == "correct":         existing.correct += count
                existing.save()
                continue  # next Translation


            # No LearningTrace for this Translation exists for the current LangySession
            # Prepare to create a new LearningTrace object

            # Attempt to find previous LearningTrace outside of this LangySession
            prev = (request.user.traces
                .filter(~Q(session = langy_session))
                .filter(translation__foreign_language = foreign_language)
                .filter(translation__id = id)
                .last())
            
            # Prepare statistics for new LearningTrace
            if prev is None:
                # New statistics
                seen = 0
                interacted = 0
                tested = 0
                correct = 0
            else:
                # Take existing statistics into account
                seen = prev.seen
                interacted = prev.interacted
                tested = prev.tested
                correct = prev.correct
            
            # Update appropriate statistic based on tracking mode
            if mode == "seen":              seen += count
            elif mode == "interacted":      interacted += count
            elif mode == "tested":          tested += count
            elif mode == "correct":         correct += count
            
            # Create new LearningTrace object
            LearningTrace.objects.create(
                user = request.user,
                session = langy_session,
                # Tracing
                translation = translation,
                prev = prev,
                # Statistics
                seen = seen,
                interacted = interacted,
                tested = tested,
                correct = correct,
            )

        return JsonResponse({"success": True})

    else:
        return HttpResponseBadRequest('Invalid request method')
