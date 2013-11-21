#!/usr/bin/env python3

# Copyright 2014 ihptru (Igor Popov)
#
# This file is part of OpenRA-Map-Stats, which is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import urllib.request
import json
import os
import sqlite3

def start():
    urllib.request.urlretrieve("http://master.open-ra.org/db/openra.db", "openra.db")
    conn = sqlite3.connect('openra.db')   # connect to database
    cur = conn.cursor()

    content = """
    <html>
    <head>
    <title>OpenRA Map's Statistics</title>
    <style type="text/css">
        body {
            font: 12px/16px Verdana, Arial, Helvetica;
        }

        #main {
            font-family: monospace;
            margin: auto;
            padding:auto;
            text-align: center;
            max-width:700px;
        }

        a:visited {
            color: #0000FF;
        }

        a:link {
            color: #0000FF;
        }

        a:hover {
            background-color:#FFFF00;
        }

        table {
            border: 2px solid #0000FF;
        }
        
        td {
            border: 2px solid #0000FF;
            padding: 2px 2px 2px 2px;
        }
        
        .players {
            color: #0000FF;
            text-decoration: underline;
        }
        
        .title {
            color: #ff7800;
        }
        
        .info {
            text-decoration: underline;
        }
        
        img {
            border: 0px;
        }
    </style>
    </head>
    <body>
    <div id="main">
        <h2><u>Mostly played OpenRA maps</u></h2>
        <i>last updated %s</i><br><br>
    </div>
    <table id="main">
        <tr>
            <td>minimap</td>
            <td>info</td>
            <td>games</td>
        </tr>
    """ % (time.strftime('%Y-%m-%d'), )

    sql = """SELECT map,count(map) as counts, avg(players) as players FROM servers
                WHERE players > 1
            GROUP BY map
            ORDER BY counts DESC LIMIT 100
    """
    cur.execute(sql)
    records = cur.fetchall()
    conn.commit()
    for i in range(len(records)):
        try:
            url = "http://content.open-ra.org/api/map_data.php?load=%s" % records[i][0]
            data = urllib.request.urlopen(url).read().decode('utf-8')
        except:
            continue
        if ( data.strip() == "-1" ):
            continue
        y = json.loads(data)
        link = y[0]['url']
        minimap = os.path.dirname(y[0]['url']) + "/minimap.bmp"

        url = "http://content.open-ra.org/api/map_data.php?hash=%s" % records[i][0]
        data = urllib.request.urlopen(url).read().decode('utf-8')
        y = json.loads(data)

        if ( y[0]['description'].strip() == "" ):
            desc = "none"
        else:
            desc = y[0]['description']
        content += """
            <tr><td><a href="http://content.open-ra.org/index.php?p=detail&table=maps&id={0}"><img src="{1}" /></a></td>
        """.format(y[0]['id'], minimap)
        content += """
            <td><span class="title">title:</span> {0}<br><span class="title">description:</span> {1}<br><span class="title">author:</span> {2}<br><span class="title">mod:</span> {3}<br><span class="info">This map is played on an average with <span class="players">{4}</span> players</span><br><a href="{5}">download</a></td>
        """.format(y[0]['title'], desc, y[0]['author'], y[0]['mod'], round(float(records[i][2])), link)
        content += """
            <td>{0}</td></tr>
        """.format(records[i][1])
    content += """
    </table>

    </body>
    </html>
    """

    file = open('index.html', 'w')
    file.writelines(content)
    file.close()

start()
