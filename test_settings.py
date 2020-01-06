GITHUB_WEBHOOK_SECRET = 'abc'
GITHUB_ACCESS_TOKEN = '123'

WATCH_CONFIG = {
    'a/b': {
        'patterns': ['documents/*', ],
        'recipients': 'nobody@example.com',
    },
    'b/*': {
        'patterns': ['documents/*', ],
        'recipients': 'nobody@example.com',
    },
    'c/d': {
        'patterns': ['documents/*', ],
        'recipients': 'nobody@example.com',
        'notify_for_private_repos': True,
    }
}
