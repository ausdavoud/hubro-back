import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from people.models import Team
from production.models import Factory


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("web socket accepted")
        self.accept()
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_object = Team.objects.filter(name=self.room_name).first()
        room_exists = bool(self.room_object)
        if not room_exists:
            async_to_sync(
                self.send(
                    text_data=json.dumps(
                        {
                            "response": {
                                "response_type": "error",
                                "message": "The team does not exists.",
                            }
                        }
                    )
                )
            )
            self.close()
            return

        print(self.scope["user"])
        if isinstance(self.scope["user"], AnonymousUser):
            async_to_sync(
                self.send(
                    text_data=json.dumps(
                        {
                            "response": {
                                "response_type": "error",
                                "message": "You are not logged in.",
                            }
                        }
                    )
                )
            )
            self.close()
            return

        is_user_room_member = self.scope["user"].player.team == self.room_object
        print(self.scope["user"].player.team)
        if not is_user_room_member:
            async_to_sync(
                self.send(
                    text_data=json.dumps(
                        {
                            "response": {
                                "response_type": "error",
                                "message": "You are not a member of this group.",
                            }
                        }
                    )
                )
            )
            self.close()
            return

        if room_exists and is_user_room_member:
            async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
            response = {"message": f'Welcome to the chat {self.scope["user"]}'}
            self.send(text_data=json.dumps({"response": response}))

    def disconnect(self, code):
        # return super().disconnect(code)
        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)

    def receive(self, text_data=None):
        text_data_json = json.loads(text_data)
        action = text_data_json["action"]
        data = text_data_json["data"]
        response = dict()
        match action:
            case "add_factory":
                response = add_factory(self, data)
            case "update_factory":
                response = update_factory(self, data)
            case _:
                response = {"message": action}
        async_to_sync(self.channel_layer.group_send)(self.room_name, {"type": "chat.message", "response": response})

    def chat_message(self, event):
        response = event["response"]
        self.send(text_data=json.dumps({"response": response}))


def add_factory(self: ChatConsumer, data):
    name = data["name"]
    price = data["price"]
    factory = Factory(name=name, price=price)
    factory.save()

    serialized_factory = {}  # FactorySerializer(instance=factory)
    return {
        "response_type": "data",
        "factory": serialized_factory.data,
        "message": "factory was saved.",
    }


def update_factory(self: ChatConsumer, data):
    name = data["name"]
    price = data["price"]
    factory = Factory.objects.filter(name=name).first()
    if not factory:
        return {"response_type": "error", "message": "factory was not found"}
    factory.price = price
    factory.save()

    serialized_factory = {}  # FactorySerializer(instance=factory)

    return {
        "response_type": "data",
        "factory": serialized_factory.data,
        "message": f"factory price was updated to {price}",
    }
