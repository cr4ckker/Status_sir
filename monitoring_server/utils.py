def jsonify_update(data):
    slots = ['id', 'server_id', 'service_name', 'severity', 'title', 'text', 'timestamp']
    return {key:data[i] for i, key in enumerate(slots)}