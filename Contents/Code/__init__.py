ICON = 'icon-default.png'
NAME = 'Radio'
PREFIX = '/music/radio'

REGEX_PLAYLIST_PLS = Regex('File1=(https?://.+)')

def Start():
    Plugin.AddViewGroup('Main Menu', viewMode='List', mediaType='items')

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
        thumb=R(station['icon']),
        key=Callback(CreateTrackObject, station=station, include_container=True),
        rating_key=station['title'],
        title=station['title'],
        items=map(CreateMediaObject, station['streams'])
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

def CreateMediaObject(stream):
    if stream['protocol'] == 'hls':
        return CreateMediaObjectHls(stream)
    elif stream['protocol'] == 'http':
        return CreateMediaObjectHttp(stream)

def CreateMediaObjectHls(stream):
    part = PartObject(key=HTTPLiveStreamURL(url=stream['url']), container='mpegts')
    part.streams.append(AudioStreamObject(codec=AudioCodec.AAC, bitrate=stream['bitrate']))
    return MediaObject(
        protocol='hls',
        container='mpegts',
        video_codec=None,
        optimized_for_streaming=True,
        bitrate=stream['bitrate'],
        parts=[part],
    )

def CreateMediaObjectHttp(stream):
    return MediaObject(
        optimized_for_streaming=True,
        parts=[PartObject(key=Callback(PlayAudioFunc(stream['playlist']), url=stream['url'], ext=stream['codec']))],
        protocol='http',
        container=stream['container'],
        audio_codec=stream['codec'],
        bitrate=stream['bitrate']
    )

def PlayAudioFunc(playlist):
    if playlist == 'pls':
        return PlayAudioPls
    elif playlist == 'm3u':
        return PlayAudioM3u

def PlayAudioPls(url):
    content = HTTP.Request(url, cacheTime=0).content
    file_url = REGEX_PLAYLIST_PLS.search(content)

    if file_url:
        stream_url = file_url.group(1)
        if stream_url[-1] == '/':
            stream_url += ';'
        else:
            stream_url += '/;'
        return Redirect(stream_url)
    else:
        raise Ex.MediaNotAvailable

def PlayAudioM3u(url):
    content = HTTP.Request(url, cacheTime=0).content
    stream_url = content.split('\n', 1)[0]
    return Redirect(stream_url)
