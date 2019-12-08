# -*- coding: utf-8 -*-
import time
import json
import requests
import urllib3


class Request(object):
    def __init__(self, url, login='', password='', cookies='', headers=''):
        self.url = url
        self.login = login
        self.password = password
        self.cookies = cookies
        self.headers = headers

    def get(self, url_param='', params='', no_check=False):
        """
        :param params: additional parameters for request
        :param url_param: part of url to add to domain url
        :param no_check: True - no need to check the status code, False - check the request response
        :return:
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        url_param = ['/' + url_param, url_param][url_param == '' or url_param.startswith('?')]

        # if there is read timeout error occurred, try to send the request 5 times then raise the exception
        for i in range(6):
            try:
                response = requests.get(self.url + url_param, params=params, cookies=self.cookies, headers=self.headers,
                                        timeout=5, verify=False)
            except Exception as t:
                if i == 5:
                    raise t
                time.sleep(1)
            else:
                # leave the loop if there is no timeout
                break

        if no_check:
            return response

        if response.status_code in [200, 202]:
            return json.loads(response.content, encoding='utf-8')
        else:
            assert (response.status_code == 200), 'Fail: GET request failure: status %s, message %s' % \
                                                  (response.status_code, response.content)

    def post(self, body, url_param='', no_check=False):

        url_param = ['/' + url_param, url_param][url_param == '']

        response = requests.post(self.url + url_param, data=body, headers=self.headers)

        if no_check:
            return response

        if response.status_code in [200, 202]:
            if response.content:
                return json.loads(response.content)
            else:
                return response.content
        else:
            assert (response.status_code == 200), 'Fail: POST request failure: status %s, message %s' % \
                                                  (response.status_code, response.content)

    def put(self, body=None, url_param='', no_check=False):

        url_param = ['/' + url_param, url_param][url_param == '']

        response = requests.put(self.url + url_param, data=body, headers=self.headers)

        if no_check:
            return response

        if response.status_code in [200, 202]:
            if response.content:
                return json.loads(response.content)
            else:
                return response.content
        else:
            assert (response.status_code == 200), 'Fail: PUT request failure: status %s, message %s' % \
                                                  (response.status_code, response.content)

    def delete(self, url_param='', params='', no_check=False):
        """
        :param params: additional parameters for request
        :param url_param: part of url to add to domain url
        :param no_check: True - no need to check the status code, False - check the request response
        :return:
        """
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        url_param = ['/' + url_param, url_param][url_param == '']

        response = requests.delete(self.url + url_param, params=params, cookies=self.cookies, headers=self.headers,
                                   verify=False)

        if no_check:
            return response

        if response.status_code in [200, 202, 204]:
            if response.content:
                return json.loads(response.content)
            else:
                return response.content
        else:
            assert (response.status_code in [200, 202, 204]), 'Fail: DELETE request failure: status %s, message %s' % \
                                                              (response.status_code, response.content)
