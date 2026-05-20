import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Comment

COMMENTS_GROUP = 'cbi_comments'


class CommentsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(COMMENTS_GROUP, self.channel_name)
        await self.accept()
        comments = await self._get_comments()
        await self.send(text_data=json.dumps({'type': 'init', 'comments': comments}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(COMMENTS_GROUP, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        username = (data.get('username') or '').strip()[:50]
        text = (data.get('text') or '').strip()[:500]

        if not username or not text:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Заполните позывной и текст версии',
            }))
            return

        comment = await self._save_comment(username, text)

        await self.channel_layer.group_send(
            COMMENTS_GROUP,
            {'type': 'broadcast_comment', 'comment': comment},
        )

    async def broadcast_comment(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'comment': event['comment'],
        }))

    # ── DB helpers ──────────────────────────────────────────────────────────

    @database_sync_to_async
    def _get_comments(self):
        return [c.to_dict() for c in Comment.objects.order_by('-created_at')[:100]]

    @database_sync_to_async
    def _save_comment(self, username, text):
        return Comment.objects.create(username=username, text=text).to_dict()
