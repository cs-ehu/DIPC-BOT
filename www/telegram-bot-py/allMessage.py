# -*- coding: utf-8 -*-


commands = {
                'start_BeforeAuthorized': 
                    u'Welcome to DIPC_Bot\n\n'
                    u'Use /on to login with your DIPC SSH credentials\n'
                    u'else - contact with an admin',

                'start_AfterAuthorized': 
                    u'Hello!\n'
                    u'Use /help to see a list of available commands',

                'help_BeforeAuthorized': 
                    u'If you have a DIPC account - use /on\n'
                    u'else - contact with an admin',

                'help_AfterAuthorized':
                    u'Commands:\n'
                    u'/off - logout\n'
                    u'/connect - Connect to a cluster\n'
                    u'/howto - User guide\n'
                    u'/information - Show information, about ssh-connection\n'
                    u'/aboutBot - Information about bot and author\n'
                    u'The following commands are only allowed if you are connected to a cluster:\n'
                    u'/consumption - Check current consumption\n'
                    u'/queue - Show job queue\n'
                    u'/scratch - See used scratch space\n'
                    u'/dcrab - See dcrab report of a job\n',

                'aboutBot': 'Bot created by DIPC to be able to connect to it\'s servers with Telegram.\n'
                    'Based on a bot made by vzemtsov - https://github.com/vzemtsov\n',

                'howto':
                    'User guide:\n'
                    u'This bot lets you connect to DIPC\'s servers with Telegram.\n'
                    u'You must have an active user account.\n'
                    u'You can execute some terminal commands writing them and\n'
                    u'sending the message. e.g.: \'cd /scratch\' or \'ls\'\n'
                    u'Some other functionalities are available too,\n'
                    u'use /help to see a list of available commands.\n',
}
