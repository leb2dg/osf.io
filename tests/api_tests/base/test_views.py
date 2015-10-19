# -*- coding: utf-8 -*-
import httplib as http
import sys
import inspect
import pkgutil

import mock

from nose import SkipTest
from nose.tools import *  # flake8: noqa

from rest_framework import generics
from rest_framework.test import (
    APIRequestFactory,
    force_authenticate
)

from tests.base import ApiTestCase
from tests import factories

import api
from api.base.settings.defaults import API_BASE
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.base.permissions import TokenHasScope
from website.settings import DEBUG_MODE

from framework.auth.oauth_scopes import CoreScopes

class TestApiBaseViews(ApiTestCase):

    def test_root_returns_200(self):
        res = self.app.get('/{}'.format(API_BASE))
        assert_equal(res.status_code, 200)

    def test_does_not_exist_returns_404(self):
        res = self.app.get('/{}{}'.format(API_BASE,"notapage"), expect_errors=True)
        assert_equal(res.status_code, 404)

    def test_does_not_exist_formatting(self):
        if DEBUG_MODE:
            raise SkipTest
        else:
            url = '/{}{}/'.format(API_BASE, 'notapage')
            res = self.app.get(url, expect_errors=True)
            errors = res.json['errors']
            assert(isinstance(errors, list))
            assert_equal(errors[0], {'detail': 'Not found.'})        

    def test_view_classes_have_minimal_set_of_permissions_classes(self):
        base_permissions = [            
            TokenHasScope,
            (IsAuthenticated, IsAuthenticatedOrReadOnly)
        ]
        view_modules = [name for _, name, _ in pkgutil.iter_modules(['api'])]
        for module in view_modules:
            if module == 'base':
                continue  # We don't need to check base urls
            urls = getattr(api, module).urls
            for patt in urls.urlpatterns:
                if not patt.callback:
                    import ipdb; ipdb.set_trace()
                view = patt.callback.cls
                for cls in base_permissions:
                    if isinstance(cls, tuple):
                        has_cls = any([c in view.permission_classes for c in cls])
                        assert_true(has_cls, "{0} lacks the appropriate permission classes".format(name))
                    else:
                        assert_in(cls, view.permission_classes, "{0} lacks the appropriate permission classes".format(name))
                for key in ['read', 'write']:
                    scopes = getattr(view, 'required_{}_scopes'.format(key), None)
                    assert_true(bool(scopes))
                    for scope in scopes:
                        assert_is_not_none(scope)

    @mock.patch('framework.auth.core.User.is_confirmed', mock.PropertyMock(return_value=False))
    def test_unconfirmed_user_gets_error(self):

        user = factories.AuthUserFactory()

        res = self.app.get('/{}nodes/'.format(API_BASE), auth=user.auth, expect_errors=True)
        assert_equal(res.status_code, http.BAD_REQUEST)
        
    @mock.patch('framework.auth.core.User.is_disabled', mock.PropertyMock(return_value=True))
    def test_disabled_user_gets_error(self):

        user = factories.AuthUserFactory()

        res = self.app.get('/{}nodes/'.format(API_BASE), auth=user.auth, expect_errors=True)
        assert_equal(res.status_code, http.BAD_REQUEST)


class TestJSONAPIBaseView(ApiTestCase):

    def setUp(self):
        super(TestJSONAPIBaseView, self).setUp()

        self.user = factories.AuthUserFactory()
        self.node = factories.ProjectFactory(creator=self.user)
        self.url = '/{0}nodes/{1}/'.format(API_BASE, self.node._id)
        for i in range(5):
            factories.ProjectFactory(parent=self.node, creator=self.user)
        for i in range(5):
            factories.ProjectFactory(parent=self.node)

    @mock.patch('api.base.serializers.JSONAPISerializer.to_representation', autospec=True)    
    def test_request_added_to_serializer_context(self, mock_to_representation):
        self.app.get(self.url, auth=self.user.auth)
        assert_in('request', mock_to_representation.call_args[0][0].context)


