import wikipedia
import urllib

def getSummary(name):
    try:
        if urllib.request.urlopen('https://en.wikipedia.org/wiki/'+name).getcode() != 404:
            return wikipedia.summary(name, sentences=5)
        else:
            return 'This nation has no information'
    except wikipedia.DisambiguationError as e:
        if len(e.options) > 0:
            return getSummary(e.options[0])
        else:
            return 'This nation has no information'
    except:
        return 'This nation has no information'
