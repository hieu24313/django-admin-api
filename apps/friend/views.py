from itertools import chain

from django.db.models import Q
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.friend.models import Interaction
from apps.friend.serializers import InforUserSerializer
from apps.general.models import DevSetting
from apps.user.models import FriendShip, CustomUser, Block
from apps.user.serializers import FriendShipSerializer, UserFriendShipSerializer, UserSerializer, \
    BaseInforUserSerializer
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_limit_offset
from ultis.socket_friend_helper import send_noti_add_friend, send_noti_accept_friend
from django.core.cache import cache


# Create your views here.
class RequestFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        list_request_friend_ship = FriendShip.objects.filter(receiver=request.user,
                                                             status='PENDING').order_by('-created_at')
        serializer = FriendShipSerializer(list_request_friend_ship, many=True, context={'request': request})
        return serializer.data, 'Danh sách lời mời kết bạn!', status.HTTP_200_OK


class ListFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        accepted_friendships = FriendShip.objects.filter(
            Q(sender=request.user, status='ACCEPTED') | Q(receiver=request.user, status='ACCEPTED')
        ).order_by('-updated_at')
        related_users = []
        for friendship in accepted_friendships:
            if friendship.sender == request.user:
                # Nếu user là sender, lấy thông tin receiver của FriendShip
                related_users.append(friendship.receiver)
            elif friendship.receiver == request.user:
                # Nếu user là receiver, lấy thông tin sender của FriendShip
                related_users.append(friendship.sender)
        serializer = UserFriendShipSerializer(related_users, many=True, context={'request': request})

        return serializer.data, 'Danh sách bạn bè!', status.HTTP_200_OK


class AddFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        receiver = CustomUser.objects.get(id=user_id)
        queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=user_id) |
                                             Q(sender_id=user_id, receiver=request.user))
        check_friend_ship = queryset.exists()

        if check_friend_ship:  # đã từng gửi yêu cầu nhưng bị hủy kết bạn hoặc từ chối sẽ vào case này
            friend_ship = queryset[0]

            if friend_ship.status == 'PENDING':
                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Đã gửi yêu cầu kết bạn rồi. Vui lòng đợi phản hồi!', status.HTTP_200_OK

            elif friend_ship.status == 'ACCEPTED':
                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Các bạn đã là bạn bè!', status.HTTP_200_OK

            else:
                friend_ship.status = 'PENDING'
                friend_ship.save()
                send_noti_add_friend(request.user, receiver, friend_ship.status, request)
                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Gửi yêu cầu kết bạn thành công!', status.HTTP_200_OK

        else:
            friend_ship = FriendShip.objects.create(sender=request.user, receiver_id=user_id)
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            send_noti_add_friend(request.user, receiver, friend_ship.status, request)

            return serializer.data, 'Gửi yêu cầu kết bạn thành công!', status.HTTP_200_OK


class AcceptFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        friend_ship = FriendShip.objects.get(id=pk)
        if friend_ship.status == 'PENDING':
            friend_ship.status = 'ACCEPTED'
            friend_ship.save()

            friend_ship.sender.count_friend += 1
            friend_ship.receiver.count_friend += 1

            friend_ship.sender.save()
            friend_ship.receiver.save()

            send_noti_accept_friend(friend_ship.sender, friend_ship.receiver, friend_ship.status, request)
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Đã chấp nhận lời mời kết bạn!', status.HTTP_200_OK

        elif friend_ship.status == 'ACCEPTED':

            return {}, 'Các bạn đã là bạn bè của nhau!', status.HTTP_200_OK

        else:
            return {}, 'Chưa gửi yêu cầu kết bạn!', status.HTTP_400_BAD_REQUEST


class AcceptFriendByUserIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=user_id) |
                                             Q(sender_id=user_id, receiver=request.user),
                                             status='PENDING')
        if queryset.exists():
            friend_ship = queryset[0]
            friend_ship.status = 'ACCEPTED'
            friend_ship.save()

            friend_ship.sender.count_friend += 1
            friend_ship.receiver.count_friend += 1

            friend_ship.sender.save()
            friend_ship.receiver.save()

            send_noti_accept_friend(friend_ship.sender, friend_ship.receiver, friend_ship.status, request)
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Đã chấp nhận lời mời kết bạn!', status.HTTP_200_OK
        else:
            return {}, 'Chưa yêu cầu kết bạn!', status.HTTP_400_BAD_REQUEST


class RejectFriendByUserIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=user_id) |
                                             Q(sender_id=user_id, receiver=request.user),
                                             status='PENDING')

        if queryset.exists():
            friend_ship = queryset[0]
            friend_ship.status = 'REJECTED'
            friend_ship.save()
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Từ chối kết bạn thành công!', status.HTTP_200_OK
        else:
            return {}, 'Yêu cầu kết bạn không tồn tại!', status.HTTP_400_BAD_REQUEST


class RejectFriendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        friend_ship = FriendShip.objects.get(id=pk)
        if friend_ship.status == 'PENDING':
            friend_ship.status = 'REJECTED'
            friend_ship.save()

            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Từ chối kết bạn thành công!', status.HTTP_200_OK
        else:
            return {}, 'Yêu cầu kết bạn không tồn tại!', status.HTTP_400_BAD_REQUEST


class DeleteFriendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        friend_ship = FriendShip.objects.get(id=pk)
        if friend_ship.status == 'ACCEPTED':
            friend_ship.status = 'DELETED'
            friend_ship.save()

            friend_ship.sender.count_friend -= 1
            friend_ship.receiver.count_friend -= 1

            friend_ship.sender.save()
            friend_ship.receiver.save()

            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Xóa bạn bè thành công!', status.HTTP_200_OK
        else:
            return {}, 'Chưa kết bạn!', status.HTTP_400_BAD_REQUEST


class DeleteFriendByUserIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request):
        user_id = request.data.get('user_id')
        queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=user_id) |
                                             Q(sender_id=user_id, receiver=request.user),
                                             status='ACCEPTED')
        if queryset.exists():
            friend_ship = queryset[0]
            friend_ship.status = 'DELETED'
            friend_ship.save()

            friend_ship.sender.count_friend -= 1
            friend_ship.receiver.count_friend -= 1

            friend_ship.sender.save()
            friend_ship.receiver.save()

            return {}, 'Xóa thành công!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Chưa kết bạn!', status.HTTP_400_BAD_REQUEST


class IsFriendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        user_id = request.data.get('user_id')
        queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=user_id) |
                                             Q(sender_id=user_id, receiver=request.user),
                                             status='ACCEPTED').exists()
        if queryset:
            return True, 'Là bạn bè!', status.HTTP_200_OK
        else:
            return False, 'Chưa là bạn bè!', status.HTTP_400_BAD_REQUEST

    # =======================  Recommended =============================


class FriendCommendedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        # r_qs = CustomUser.custom_objects.filter_blocked_users(request.user)

        # Now, call get_recommendations() method to get the recommended users
        # Check information similarity here
        # r_qs = get_similar_profiles(r_qs, request.user)
        r_qs = CustomUser.custom_objects.recommend_users_and_weight(request.user)
        final_data, paginator = get_paginator_limit_offset(r_qs, request)

        serializer = InforUserSerializer(final_data, many=True, context={'request': request})
        paginator_data = paginator.get_paginated_response(serializer.data).data

        return paginator_data, "Danh sách đề cử", status.HTTP_200_OK


class FriendNearbyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):

        list_user_no_block = CustomUser.custom_objects.filter_blocked_users(request.user)
        if request.user in list_user_no_block:
            # Loại bỏ người dùng hiện tại khỏi danh sách
            list_user_no_block = list_user_no_block.exclude(id=request.user.id)

        gender = request.query_params.get('gender_list').split(',') if request.query_params.get('gender_list') else None
        from_age = request.query_params.get('from_age', None)
        to_age = request.query_params.get('to_age', None)
        from_height = request.query_params.get('from_height', None)
        to_height = request.query_params.get('to_height', None)
        from_weight = request.query_params.get('from_weight', None)
        to_weight = request.query_params.get('to_weight', None)
        from_distance = request.query_params.get('from_distance', 0)
        to_distance = request.query_params.get('to_distance', 20)
        search = request.query_params.get('search').split(',') if request.query_params.get('search') else None

        list_user_no_block = list_user_no_block.filter(
            baseinformation__search__id__in=search).distinct() if search else list_user_no_block

        list_user_no_block = list_user_no_block.filter(gender__in=gender) if gender else list_user_no_block

        list_user_no_block = list_user_no_block.filter(
            age__range=[int(from_age), int(to_age)]) if from_age else list_user_no_block

        list_user_no_block = list_user_no_block.filter(
            height__range=[int(from_height), int(to_height)]) if from_height else list_user_no_block

        list_user_no_block = list_user_no_block.filter(
            weight__range=[int(from_weight), int(to_weight)]) if from_weight else list_user_no_block

        if request.user.lat:  # filter theo lat lng
            serializer_data = InforUserSerializer(list_user_no_block, many=True, context={'request': request}).data
            final_users = []
            for user in serializer_data:
                if user['distance'] is not None and float(from_distance) <= user['distance'] <= float(to_distance):
                    final_users.append(user)
            final_data, paginator = get_paginator_limit_offset(final_users, request)
            paginator_data = paginator.get_paginated_response(final_data).data

            return paginator_data, "Danh sách gần đây", status.HTTP_200_OK

        else:  # filter theo tỉnh

            list_user_no_block = list_user_no_block.filter(province=request.user.province)
            final_data, paginator = get_paginator_limit_offset(list_user_no_block, request)

            serializer_data = InforUserSerializer(final_data, many=True, context={'request': request}).data
            paginator_data = paginator.get_paginated_response(serializer_data).data

            return paginator_data, "Danh sách gần đây", status.HTTP_200_OK


class FriendMatchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        # # List user like request user
        # liked_qs = Interaction.objects.filter(to_user_id=request.user.id,
        #                                       status='LIKE').values_list('from_user', flat=True)
        # liked_interaction = []
        # for like in liked_qs:
        #     i, created = Interaction.objects.get_or_create(to_user_id=like,
        #                                                    from_user_id=request.user.id,
        #                                                    )
        #     if i.status == 'PENDING':
        #         liked_interaction.append(i.to_user.id)
        # # List user match with request user
        # r_qs = CustomUser.custom_objects.recommend_users(request=request)
        # pending_qs = []
        # unlike_qs = []
        # like_qs = []
        # for r in r_qs:
        #     i, created = Interaction.objects.get_or_create(to_user_id=r.id,
        #                                                    from_user_id=request.user.id,
        #                                                    )
        #     user_id = i.to_user.id
        #
        #     if i.status == 'UNLIKE':
        #         unlike_qs.append(user_id)
        #     elif i.status == 'LIKE':
        #         like_qs.append(user_id)
        #     else:
        #         pending_qs.append(user_id)
        #
        # liked_qs = CustomUser.objects.filter(id__in=liked_interaction)
        # pending_qs = CustomUser.objects.filter(id__in=pending_qs)
        # unlike_qs = CustomUser.objects.filter(id__in=unlike_qs)
        # like_qs = CustomUser.objects.filter(id__in=like_qs)
        #
        # merge_qs = list(chain(liked_qs, pending_qs, unlike_qs, like_qs))
        qs_match = CustomUser.custom_objects.recommend_users(request.user)
        serializer = InforUserSerializer(qs_match, many=True, context={'request': request})
        return serializer.data, "Danh sách ghép đôi", status.HTTP_200_OK

    @api_decorator
    def post(self, request, pk):
        new_status = request.data.get('status')
        interaction, created = Interaction.objects.get_or_create(to_user_id=pk,
                                                                 from_user_id=request.user.id,
                                                                 )
        interaction.set_status(new_status)
        return {}, "Tương tác thành công", status.HTTP_200_OK


class FindUserByFullName(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        name = request.query_params.get('name')
        user_rs = CustomUser.custom_objects.filter_blocked_users(request.user)
        final_queryset = user_rs.filter(full_name__icontains=name)
        serializer = InforUserSerializer(final_queryset, many=True, context={'request': request})
        return serializer.data, 'Danh sách kết quả', status.HTTP_200_OK


class RevokeRequestFriend(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        friend_ship = FriendShip.objects.get(id=pk)

        if friend_ship.status == 'PENDING':
            friend_ship.status = 'DELETED'
            friend_ship.save()
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Thu hồi lời mời kết bạn thành công!', status.HTTP_200_OK

        elif friend_ship.status == 'REJECTED':
            return {}, 'Đối phương đã từ chối kết bạn!', status.HTTP_400_BAD_REQUEST

        elif friend_ship.status == 'ACCEPTED':
            return {}, 'Đối phương đã chấp nhận lời mời kết bạn!', status.HTTP_400_BAD_REQUEST


class RevokeRequestFriendByUserID(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')

        friend_ship = FriendShip.objects.filter(sender=request.user, receiver_id=user_id)[0]

        if friend_ship.status == 'PENDING':
            friend_ship.status = 'DELETED'
            friend_ship.save()
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Thu hồi lời mời kết bạn thành công!', status.HTTP_200_OK

        elif friend_ship.status == 'REJECTED':
            return {}, 'Đối phương đã từ chối kết bạn!', status.HTTP_400_BAD_REQUEST

        elif friend_ship.status == 'ACCEPTED':
            return {}, 'Đối phương đã chấp nhận lời mời kết bạn!', status.HTTP_400_BAD_REQUEST
