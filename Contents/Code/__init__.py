ICON = 'icon-default.png'
NAME = 'Radio'
PREFIX = '/music/radio'

def Start():
    Plugin.AddViewGroup('Main Menu', viewMode = 'List', mediaType = 'items')

    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = 'Main Menu'

    TrackObject.thumb = R(ICON)

@handler(PREFIX, NAME)
def MainMenu():
    oc = ObjectContainer()
    for station in Dict['stations']:
        oc.add(CreateTrackObject(station=station))
    return oc

def CreateTrackObject(station, include_container=False):
    track_object = TrackObject(
        key = Callback(CreateTrackObject, station=station, include_container=True),
        rating_key = station['url'],
        title = station['title'],
        items = [
            MediaObject(
                optimized_for_streaming=True,
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(url=station['url'])
                    )
                ]
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

