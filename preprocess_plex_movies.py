import os
from importlib import import_module
from pathlib import Path
from plexapi.server import PlexServer

plex_set_tracks = import_module("plex-audio-subtitle-switcher")
from subaligner.utils import Utils
extract = Utils().extract_matroska_subtitle

baseurl = os.environ.get('PLEX_URL')
token = os.environ.get('PLEX_TOKEN')
plex = PlexServer(baseurl, token)

indexes = {}
library = plex.library.section('Movies')
movies = library.search(libtype="movie")
template = ""
replacement = ""
for movie in movies:
    audio_channel = None
    subtitle_channel = None
    movie.reload()
    part = movie.media[0].parts[0]
    path = part.file.replace(template, replacement)
    if not os.path.exists(path + '.srt'):
        if part.file.endswith('.mkv') or part.file.endswith('.mp4'):
            streams = plex_set_tracks.OrganizedStreams(part)
            try:
                langs = sorted(list(set([x.languageCode for x in streams.audioStreams])))
            except:
                continue
            if len(langs) == 2 and len(set(langs)) == 2:
                if movie.useOriginalTitle == movie.title:
                    continue

            count = 0
            for stream in streams.audioStreams:
                if stream.languageCode == 'eng':
                    audio_channel = count
                count += 1

            if len(streams.internalSubs) > 0:
                count = 0
                subs = streams.internalSubs
                langs = [x.languageCode for x in subs]
                inds = [i for i, x in enumerate(langs) if x == 'eng' and not subs[i].forced]
                temp = [x for x in range(len(subs))]
                titles = [subs[i].extendedDisplayTitle.lower() for i in inds]
                scores = [1] * len(titles)
                for i, title in enumerate(titles):
                    if 'full' in title:
                        scores[i] *= 2
                    if 'pgs' in title:
                        scores[i] *= -1

                if len(scores) > 0:
                    max_ind, _ = max(enumerate(scores), key=lambda x: x[1])
                    if scores[max_ind] > 0:
                        subtitle_channel = temp[inds[max_ind]]
                        if subtitle_channel is not None and audio_channel is not None:
                            assert subtitle_channel >= 0
                            assert audio_channel >= 0

                            indexes[path] = [audio_channel, subtitle_channel]
                            # try:
                            extract(path, subtitle_channel, 600, path + '.srt')
                            # except:
                            #     continue
