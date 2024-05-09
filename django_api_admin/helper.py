import uuid


def convert_primary_key_related_uuid_to_str(data):
    def _convert_uuid(data):
        if isinstance(data, dict):
            return {key: _convert_uuid(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [_convert_uuid(item) for item in data]
        elif isinstance(data, uuid.UUID):
            return str(data)
        else:
            return data

    for field in data['fields']:
        if field.get('type') == 'PrimaryKeyRelatedField':
            choices = field['attrs'].get('choices')
            if choices:
                if isinstance(choices, dict):
                    field['attrs']['choices'] = {
                        str(uuid_key): value for uuid_key, value in choices.items()
                    }
                elif isinstance(choices, list):
                    field['attrs']['choices'] = [
                        str(uuid_choice) for uuid_choice in choices
                    ]
    return data