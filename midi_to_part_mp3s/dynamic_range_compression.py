def compress_dynamic_range(midi_data):
    return equalize_volume_change_events(
        rescale_velocities(midi_data)
    )


def equalize_volume_change_events(midi_data, constant_volume_setting=100):
    for track in midi_data.tracks:
        for message in track:
            if message.type == 'control_change' and message.control == 7:
                message.value = constant_volume_setting

    return midi_data


def rescale_velocities(midi_data):
    # full range is 0-127
    min_allowed = 55
    max_allowed = 70

    min_observed, max_observed = calibrate_existing_dynamic_range(midi_data)

    for track in midi_data.tracks:
        for message in track:
            if message.type == 'note_on' and message.velocity != 0:
                rescaled_velocity = int((max_allowed - min_allowed) *
                                        ((message.velocity - min_observed)/(max_observed - min_observed)) + min_allowed)
                message.velocity = rescaled_velocity

    return midi_data


def calibrate_existing_dynamic_range(midi_data):
    min_observed = None
    max_observed = None

    for track in midi_data.tracks:
        for message in track:
            if message.type == 'note_on':
                observation_already_made = max_observed and min_observed
                if observation_already_made:
                    max_observed = max(message.velocity, max_observed)
                    min_observed = min(message.velocity, min_observed)
                else:
                    max_observed = message.velocity
                    min_observed = message.velocity

    return min_observed, max_observed
