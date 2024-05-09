from django.db.models import Q

from apps.user.models import CustomUser, FriendShip
from apps.user.serializers import FriendShipSerializer
from ultis.user_helper import haversine


def check_update_user_cache_different(current_cache, request_user, user2):
    # Chk block
    current_block = CustomUser.custom_objects.is_block(request_user, user2)

    if current_block != current_cache['block_status']:
        current_cache['block_status'] = current_block

    # Chk distance
    try:
        current_distance = haversine(request_user.lat,
                                     request_user.lng,
                                     user2.lat,
                                     user2.lng)
    except Exception as e:
        print(e)
        current_distance = None

    if current_distance != current_cache['distance']:
        current_cache['distance'] = current_distance

    # Chk friend
    friendship = FriendShip.objects.filter(
        Q(sender=request_user, receiver=user2) |
        Q(sender=user2, receiver=request_user),
        status__in=['ACCEPTED', 'PENDING']
    ).first()
    if friendship:
        friendship = FriendShipSerializer(friendship).data
    else:
        friendship = None
    if friendship != current_cache['friend']:
        current_cache['friend'] = friendship

    return current_cache
