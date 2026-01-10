from myapps.whiteboard.agora import generate_room_token

token = generate_room_token("some-room-uuid", is_teacher=True)
print(token)

