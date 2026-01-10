# from django.test import TestCase

# # Create your tests here.

# set AGORA_APP_ID=ba25e5967aba4e959322196250dac65f
# set AGORA_REST_ID=uh90WmH02uo2GpbL
# set AGORA_REST_CERTIFICATE=W6NlmbFjSbPI7D2p8303XH_jrkrf7VNb

from myapps.whiteboard.agora import generate_room_token

token = generate_room_token("some-room-uuid", is_teacher=True)
print(token)

