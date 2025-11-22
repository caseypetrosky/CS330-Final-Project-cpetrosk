## Important Client to server packets

### Player Chat:
* 5: chat_command
* 6: chat_command_signed
* 7: chat_message
* 8: chat_session_update

### Player movement:
28: position
29: position_look
30: look
31: flying
32: vehicle_move (boat/minecart)

### misc  ones:
26: keep_alive
51: held_item_slot (switching hotbar slot)
62: block_place
39: block_dig


## Important Server to client packets

### Chat shown to players:
58: player_chat
114: system_chat
80: action_bar (little messages above hotbar)

### Movement/world updates:
31: sync_entity_position
39: map_chunk
77: multi_block_change
87: update_view_position
88: update_view_distance

### Connection:

38: keep_alive
54: ping
55: ping_response

# First successful chat blocking
Proxy listening on 127.0.0.1:25566 -> 127.0.0.1:25565
Using Minecraft protocol 1.21.6 (play state)
New client from ('127.0.0.1', 56185)
[BLOCKED CHAT] C->S packetId=8 (chat_session_update)
[BLOCKED CHAT] C->S packetId=6 (chat_command_signed)
[BLOCKED CHAT] C->S packetId=8 (chat_session_update)
[BLOCKED CHAT] C->S packetId=8 (chat_session_update)
[BLOCKED CHAT] C->S packetId=8 (chat_session_update)
Exception in thread Thread-3 (forward):

Connection closed. Packet ID counts so far:

  (client -> server)
    ID   0 (teleport_confirm): 4
    ID   2 (select_bundle_item): 1
    ID   3 (set_difficulty): 2
    ID   6 (chat_command_signed): 1
    ID   7 (chat_message): 1
    ID   8 (chat_session_update): 4
    ID  10 (client_command): 33
    ID  12 (settings): 1059
    ID  27 (lock_difficulty): 3
    ID  29 (position_look): 102
    ID  30 (look): 4
    ID  31 (flying): 26
    ID  32 (vehicle_move): 1
    ID  41 (player_input): 4
    ID  42 (player_loaded): 10
    ID  43 (pong): 1
    ID  52 (update_command_block): 1
  (server -> client)
    ID   0 (bundle_delimiter): 628
    ID   1 (spawn_entity): 315
    ID   2 (animation): 1
    ID   3 (statistics): 1
    ID   7 (block_action): 21
    ID   8 (block_change): 28
    ID  10 (difficulty): 1
    ID  11 (chunk_batch_finished): 33
    ID  12 (chunk_batch_start): 34
    ID  13 (chunk_biomes): 1
    ID  14 (clear_titles): 1
    ID  16 (declare_commands): 1
    ID  18 (window_items): 1
    ID  34 (game_state_change): 440
    ID  35 (open_horse_window): 951
    ID  37 (initialize_world_border): 23
    ID  38 (keep_alive): 1
    ID  42 (update_light): 1
    ID  43 (login): 3
    ID  44 (map): 496
    ID  45 (trade_list): 1
    ID  48 (move_minecart): 1
    ID  51 (open_book): 8801
    ID  52 (open_window): 4372
    ID  54 (ping): 223
    ID  62 (player_remove): 1
    ID  68 (recipe_book_remove): 3
    ID  70 (entity_destroy): 1
    ID  72 (reset_score): 1
    ID  74 (add_resource_pack): 1
    ID  75 (respawn): 151
    ID  81 (world_border_center): 8573
    ID  82 (world_border_lerp_size): 263
    ID  84 (world_border_warning_delay): 1
    ID  92 (entity_metadata): 2
    ID  95 (entity_equipment): 1
    ID  97 (update_health): 486
    ID  99 (scoreboard_objective): 7045
    ID 100 (set_passengers): 53
    ID 101 (set_player_inventory): 1
    ID 102 (teams): 1
    ID 103 (scoreboard_score): 1
    ID 111 (start_configuration): 54
    ID 115 (playerlist_header): 22
    ID 125 (entity_effect): 1
    ID 126 (declare_recipes): 1
    ID 128 (set_projectile_power): 1
    ID 129 (custom_report_details): 358
    ID 131 (unknown): 1
