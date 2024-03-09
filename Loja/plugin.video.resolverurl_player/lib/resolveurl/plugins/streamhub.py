"""
    Plugin for ResolveURL
    Copyright (C) 2021 shellc0de

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from resolveurl.plugins.__resolve_generic__ import ResolveGeneric
from resolveurl.lib import helpers


class StreamHubResolver(ResolveGeneric):
    name = 'StreamHub'
    domains = ['streamhub.to', 'streamhub.gg', 'streamhub.ink', 'streamhub.top']
    pattern = r'(?://|\.)(streamhub\.(?:top?|gg|ink))/(?:embed-|e/|d/)?([0-9a-zA-Z]+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(
            self.get_url(host, media_id),
            patterns=[r'''sources:\s*\[(?:{src:)?\s*"(?P<url>[^"]+)'''],
            generic_patterns=False,
            referer=False
        )

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, template='https://{host}/e/{media_id}')
