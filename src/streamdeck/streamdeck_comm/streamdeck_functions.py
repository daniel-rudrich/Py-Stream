from StreamDeck.DeviceManager import DeviceManager
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder)


def get_streamdecks():
    streamdecks = DeviceManager().enumerate()
    return streamdecks


def init_streamdeck(deck):
    deck.open()
    deck.reset()

    print("Opened '{}' device (serial number: '{}')".format(
        deck.deck_type(), deck.get_serial_number()))

    """
    Check for Streamdeck in database.
    Create a new one with corresponding StreamdeckModel if it doesn't exist yet
    """

    if not Streamdeck.objects.filter(serial_number=deck.get_serial_number()):
        """
        Check for StreamdeckModel in database.
        Create a new one if it doesn't exist yet
        """
        if not StreamdeckModel.objects.filter(
                name=deck.deck_type()):

            keys_per_row = deck.key_count()/deck.KEY_ROWS
            StreamdeckModel.objects.create(
                name=deck.deck_type(),
                key_count=deck.key_count(),
                keys_per_row=keys_per_row
            )

        streamdeckmodel = StreamdeckModel.objects.filter(
            name=deck.deck_type())[0]
        deck.set_brightness(30)
        Streamdeck.objects.create(name=deck.deck_type(),
                                  serial_number=deck.get_serial_number(),
                                  brightness=30,
                                  streamdeck_model=streamdeckmodel
                                  )

    active_streamdeck = Streamdeck.objects.filter(
        serial_number=deck.get_serial_number())[0]

    print(active_streamdeck)

    """
    Get all keys from the default folder of the streamdeck.
    Create the keys and the folder if necessary
    """
    list_key = []
    keys = StreamdeckKey.objects.filter(streamdeck=active_streamdeck.id)
    if not keys:
        """
        Initialize folder and keys
        """
        new_folder = Folder.objects.create(name='default')

        for i in range(deck.key_count()):
            new_key = StreamdeckKey.objects.create(
                number=i,
                text="",
                folder=new_folder,
                streamdeck=active_streamdeck
            )
            list_key.append(new_key)
    else:
        """
        Get default folder id and all the corresponding keys
        (seems to complicated maybe add streamdeck as foreignkey to folder)
        """
        folder_ids = StreamdeckKey.objects.filter(
            streamdeck=active_streamdeck).values("folder").distinct()
        default_folder = Folder.objects.filter(
            id__in=folder_ids, name='default').values('id')[0]['id']
        default_keys = list(
            StreamdeckKey.objects.filter(folder=default_folder))
        print(default_keys)
        list_key.extend(default_keys)

    """
    Load all keys onto the streamdeck
    """

    """
    the streamdeck only closes here for testing purposes.
    in reality it should close when the application is stopped
    """
    deck.close()


def streamdeck_init():
    streamdecks = get_streamdecks()
    for deck in streamdecks:
        init_streamdeck(deck)


if __name__ == "__main__":
    streamdeck_init()
