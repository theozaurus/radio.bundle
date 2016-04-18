ICON = 'icon-default.png'
NAME = 'Radio'
PREFIX = '/music/radio'

CONTAINERS = {'mp4': Container.MP4, 'mp3': Container.MP3}
CODECS = {'aac': AudioCodec.AAC, 'mp3': AudioCodec.MP3}
RE_FILE = Regex('File1=(https?://.+)')

def Start():
    Plugin.AddViewGroup('Main Menu', viewMode='List', mediaType='items')

    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = 'Main Menu'

    TrackObject.thumb = R(ICON)

@handler(PREFIX, NAME)
def MainMenu():
    oc = ObjectContainer()
    for station in Dict['stations']:
        if station['hls']:
            oc.add(CreateHlsTrackObject(station=station))
        else:
            oc.add(CreateTrackObject(station=station))
    return oc

def CreateHlsTrackObject(station, include_container=False):
    track_object = TrackObject(
        key=Callback(CreateHlsTrackObject, station=station, include_container=True),
        rating_key=station['url'],
        title=station['title'],
        items=[
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

def CreateTrackObject(station, include_container=False):
    container = CONTAINERS[station['container']]
    audio_codec = CODECS[station['codec']]

    track_object = TrackObject(
        key=Callback(CreateTrackObject, station=station, include_container=True),
        rating_key=station['url'],
        title=station['title'],
        items=[
            MediaObject(
                optimized_for_streaming=True,
                parts=[
                    PartObject(key=Callback(PlayAudio, url=station['url'], ext=station['codec']))
                ],
                container=container,
                audio_codec=audio_codec,
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

def PlayAudio(url):
    content = HTTP.Request(url, cacheTime=0).content
    file_url = RE_FILE.search(content)

    if file_url:
        stream_url = file_url.group(1)
        if stream_url[-1] == '/':
            stream_url += ';'
        else:
            stream_url += '/;'
        return Redirect(stream_url)
    else:
        raise Ex.MediaNotAvailable
