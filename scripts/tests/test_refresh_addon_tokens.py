# -*- coding: utf-8 -*-

import mock
from nose.tools import *  # noqa

from tests.base import OsfTestCase

from website.addons.box.tests.factories import BoxAccountFactory
from website.addons.mendeley.tests.factories import MendeleyAccountFactory

import datetime

from dateutil.relativedelta import relativedelta

from website.oauth.models import ExternalAccount

from scripts.refresh_addon_tokens import (
    get_targets, main, look_up_provider, PROVIDER_CLASSES
)


class TestRefreshTokens(OsfTestCase):

    def setUp(self):
        super(TestRefreshTokens, self).setUp()
        self.addons = ('box', 'mendeley', )

    def tearDown(self):
        super(TestRefreshTokens, self).tearDown()
        ExternalAccount.remove()

    def test_look_up_provider(self):
        for Provider in PROVIDER_CLASSES:
            result = look_up_provider(Provider.short_name)
            assert_equal(result, Provider)
        fake_result = look_up_provider('fake_addon_name')
        assert_equal(fake_result, None)

    def test_get_targets(self):
        now = datetime.datetime.utcnow()
        records = [
            BoxAccountFactory(expires_at=now + datetime.timedelta(days=8)),
            BoxAccountFactory(expires_at=now + datetime.timedelta(days=6)),
            MendeleyAccountFactory(expires_at=now + datetime.timedelta(days=8)),
            MendeleyAccountFactory(expires_at=now + datetime.timedelta(days=6)),
        ]
        box_targets = list(get_targets(delta=relativedelta(days=-7), addon_short_name='box'))
        mendeley_targets = list(get_targets(delta=relativedelta(days=-7), addon_short_name='mendeley'))
        assert_equal(records[1]._id, box_targets[0]._id)
        assert_not_in(records[0], box_targets)
        assert_equal(records[3]._id, mendeley_targets[0]._id)
        assert_not_in(records[2], mendeley_targets)

    @mock.patch('scripts.refresh_addon_tokens.Mendeley.refresh_oauth_key')
    @mock.patch('scripts.refresh_addon_tokens.Box.refresh_oauth_key')
    def test_refresh(self, mock_box_refresh, mock_mendeley_refresh):
        fake_box_account = BoxAccountFactory(expires_at=datetime.datetime.utcnow())
        fake_mendeley_account = MendeleyAccountFactory(expires_at=datetime.datetime.utcnow())
        for addon in self.addons:
            Provider = look_up_provider(addon)
            main(delta=relativedelta(days=-7), Provider=Provider, dry_run=False)
        assert_equal(1, mock_box_refresh.call_count)
        assert_equal(1, mock_mendeley_refresh.call_count)
