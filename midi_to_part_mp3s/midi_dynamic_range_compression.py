import mido
from typing import Optional
from midi_to_part_mp3s.custom_types import MidiMessageType, MidiAttribute


def compress_midi_dynamic_range(midi_data: mido.MidiFile):
    return equalize_volume_change_events(
        rescale_appropriate_measure(midi_data)
    )


def rescale_appropriate_measure(midi_data: mido.MidiFile):
    if velocities_are_used_for_volume(midi_data):
        return rescale('note_on', 'velocity', midi_data)
    else:
        # FIXME: Use regular logging
        print("\n\n Scaling expression cc=11")
        return rescale('control_change', 'value', midi_data, control_code=11)


def equalize_volume_change_events(midi_data: mido.MidiFile,
                                  constant_volume_setting: int = 100):
    for track in midi_data.tracks:
        for message in track:
            if message.type == 'control_change' and message.control == 7:
                message.value = constant_volume_setting

    return midi_data


def velocities_are_used_for_volume(midi_data: mido.MidiFile):
    # FIXME: Find some was to use the __log function here to print out
    # fact that velocities cannot be used for dynamic range scaling.
    min_observed, max_observed = calibrate_existing_dynamic_range_for('note_on', 'velocity', midi_data)

    return min_observed != max_observed


def rescale(midi_message_type: MidiMessageType,
            midi_attribute: MidiAttribute,
            midi_data: mido.MidiFile,
            control_code=None):
    # full range is 0-127
    min_allowed = 55
    max_allowed = 70

    min_observed, max_observed = calibrate_existing_dynamic_range_for(
        midi_message_type, midi_attribute, midi_data, control_code
    )

    print("\n")
    print(min_observed)
    print("\n")
    print(max_observed)
    print("\n\n\n\n")
    for track in midi_data.tracks:
        for message in track:
            if message.type != midi_message_type:
                next
            else:
                attribute_value = getattr(message, midi_attribute)
                if attribute_value != 0:
                    rescaled_value = int((max_allowed - min_allowed) *
                                         ((attribute_value - min_observed)/(max_observed - min_observed)) + min_allowed)
                    setattr(message, midi_attribute, rescaled_value)

    return midi_data


def calibrate_existing_dynamic_range_for(midi_message_type: MidiMessageType,
                                         midi_attribute: MidiAttribute,
                                         midi_data: mido.MidiFile,
                                         control_code: Optional[int] = None):
    min_observed = None
    max_observed = None

    for track in midi_data.tracks:
        observation_already_made = max_observed is not None and min_observed is not None
        for message in track:
            if message.type == midi_message_type:
                if control_code and message.control == control_code:
                    attribute_value = getattr(message, midi_attribute)
                    if observation_already_made:
                        max_observed = max(attribute_value, max_observed)
                        min_observed = min(attribute_value, min_observed)
                    else:
                        max_observed = attribute_value
                        min_observed = attribute_value

    return min_observed, max_observed
