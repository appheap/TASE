<div class="Intro" align="center">
<h1>Telegram audio search engine (TASE)</h1>
<hr class="dashed">
<h3>A lightning fast audio full-text search engine on top of Telegram</h3>

<p>It allows users to quickly and easily find information that is of 
genuine interest or value, without the need to wade through numerous 
irrelevant channels. It provides users with search 
results that lead to relevant information on high-quality audio files.</p>

<img src="https://img.shields.io/github/workflow/status/dwyl/auth_plug/Elixir%20CI?label=build&style=plastic">
<img src="https://img.shields.io/github/stars/appheap/TASE?style=social">
<img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=plastic">
<img src="https://hits.dwyl.com/appheap/TASE.svg?style=flat&show=unique">
<img src="https://img.shields.io/github/downloads/appheap/tase/total">

</div>
<hr class="dotted">

<div>
<h2>Contents</h2>
<ul>
<h4>
<li><a href="#intro">What makes TASE special?</a></li>
<li><a href="#installation">How to install and run</a></li>
<li><a href="#features">Features</a></li>
<li><a href="#techstack">Technology stack</a></li>
<li><a href="#contribution">Call for Contributions</a></li>
<li><a href="#license">License and people</a></li>
</h4>
</ul>
</div>
<hr class="dotted">


<div>
<h2 id="intro">What makes TASE special?</h2>
<p>TASE is a growing open source full-text audio search engine platform that serves high-volume requests from 
users. Based on Python and Telegram, the latest major update introduces many new features among which 
a highly abstracted and modular design pattern powered by Elasticsearch and ArangoDB with support for parallel clusters 
on different servers located in different parts of the world.</p>

<h3>TASE at a glance</h3>
<ol>
<li>Advanced full-text search engine for audio files</li>
<li>Extremely fast audio file indexer (benchmark: minimum 4 million songs per day per client)</li>
<li>Support for multiple parallel clients as indexer</li>
<li>Support for distributed parallel clusters on multiple servers (searching and indexing) (all audio files, graph and document models)</li>
<li>Graph of users and items</li>
<li>Dynamic URLs</li>
<li>Asynchronous</li>
<li>Reach admin tools</li>
<li>Multilingual</li>
<li>Audio file caching</li>
<li>Easy configuration and customization</li>
<li>Friendly look and feel</li>
</ol>

<h3>TASE is free and always will be. Help us out… If you love free stuff and great software, give us a star!
:star::star2:</h3>
</div>

<hr class="dotted">

<div>
<h2 id="installation">How to install and run</h2>
<ul>
<i>* Note: please make sure to read the configuration and customization section before you run the project</i>
<h3>There are two different ways to use TASE</h3><div>
<ol>
<li><h4>Manually install the dependencies</h4>
    <ol>
    <li>Clone the repository</li>
    <li>Install Elasticsearch (v8.3) (<a href="">instructions</a>)</li>
    <li>Install ArangoDB (v3.9.1) (<a href="">instructions</a>)</li>
    <li><pre>poetry install</pre><i>* install <b>poetry</b> if you haven't already</i> (<a href="">instructions</a>)</li>
    <li>Run the <a href="./tase/tase_client.py">tase_client</a> file located in the <a href="./tase">tase</a> package 
    <i>(*note: before running the project make sure to configure the <a href="./tase.toml">tase.toml</a> file)</i></li>
    </ol>
</li>

<li><h4>Install using docker-compose</h4> The easier method (recommended) <i>(*note: before running the project make
sure to configure the <a href="./tase.toml">tase.toml</a> file)</i>
    <pre>docker-compose up</pre><i>* install <b>docker-compose</b> if you haven't already</i> (<a href="">instructions</a>)
</li>
</ol>
</div>

<div>
<h3>Configuration and customization</h3>
<p>Before you run your project you need to customize the <a href="./tase.toml"><b>tase.toml</b></a> file in the root directory which is used as 
the config file by TASE</p>

<p>In order to run the project you have to provide basic information which the bot works with.
For instance you must provide telegram bot token and your Telegram client authentication information 
to run your own clients.</p>
</div>
</ul>
</div>

<hr class="dotted">

<div>
<h2 id="features">Features</h2>
<h3>Features for developers</h3>
<ol>
<li>Add new languages in locales (we recommend using <a href="https://poedit.net/">Poedit</a>)</li>
<li>Easily add new buttons and functionalities (query and inline) by implementing the abstract methods in the base button class</li>
<li>Realtime visualizations for graph models and audio files (Kibana, ArangoDB)</li>
<li>Abstraction and facade design pattern</li>
</ol>
</div>
<h3>Wide Range of Features :bulb:</h3>
<ol>
<li><h4>Search engine</h4></li>
<ul>
    <li>Search audio files through the direct bot search</li>
    <li>Search audio files from groups and private chats using @bot_name mention
    and send them directly to the chat</li>
    <li>Real-time search using @bot_name mention, by showing an inline list of results</li>
    <li>Real-time search directly in the private and group chats</li>
    <li>Search based on file-name, performer name, and audio-name</li>
    <li>Shows the top 10 relevant results in a message and unlimited in the more results; returned as an inline list</li>
    <li>Play the songs in the inline lists before downloading them</li>
    <li>Caches searched audio files to avoid unnecessary redundant DB requests</li>
    <li>Dynamic URL for the results</li>
    <li>Allows the owner to trace the downloaded audio files</li>
    <li>High accuracy and relevance</li>
    <li>Search in a wide variety of languages</li>
    <li>Show the source-channel name and the link to the file</li>
    <li>Sort results in reverse mode (to make more relevant results in the bottom)</li>
</ul>
<img src="images/search.PNG" alt="Search example screenshot">
<caption align="center">Search example screenshot</caption>
<p></p><br>
<img src="images/audio.PNG">
<caption align="center">Result audio example screenshot</caption>
<br>

<li><h4>Indexing features</h4></li>
<ul>
    <li>Automatically finds new channels in an optimistic way
        (first assumes it is a valid channel and validates it later 
        before starting to index) 
        <ol>
        <li>Extract from texts and captions</li>
        <li>Extract from "forwarded mention"</li>
        <li>Extract from links</li>
        </ol>
    </li>
    <li>Automatically indexes new channels</li>
    <li>Iterates through previous channels and resumes indexing from the previous checkpoint</li>
    <li>Extremely fast indexing (minimum 4 million songs per day per client</li>
    <li>Analyzes channels and calculates a score (0-5) based on their 
        <ol>
            <li>Density of audio files (ratio of audio files</li>
            <li>Activity of the channel (how frequent it shares new files)</li>
            <li>Number of members</li>
        </ol>
    </li>
    <li>Avoids getting banned by the Telegram servers</li>
    <li>Support for parallel indexing using multiple Telegram clients</li>
    <li>Hashes the file IDs in a specific way that avoids conflicts to a high degree and still keeps them as short as eight characters</li>    
    <li>Users and channel owners can send request to index a specific channel useing "/index channel_name"</li>    
    <li>Constructs a graph for users and audio files in real time which can be used for recommendation systems and 
    link prediction tasks</li>

</ul>
<br>
<li><h4>User limiting/controlling features</h4></li>
<ul>
    <li>Handle user membership in your channel(s) in near real-time</li>
    <li>Set limitations for users based on their membership status</li>
    <li>Limits not-a-member users to search 5 audio files freely, and then they should wait for one minute until they receive their searched audio files</li>
    <li>Not members have limitations with direct in-chat searches</li>
</ul><br>
<li><h4>User interface</h4></li>
<ul>
    <li>User guide</li>
    <li>Multiple menus (home, help, playlist etc.)</li>
    <li>A keyboard for each part to ease the process for users</li>
    <li>Multilingual bot - currently supported: 
    <ul>
    <li> :us: English</li>
    <li> :es: Spanish</li>
    <li> :ru: Russian</li>
    <li> :united_arab_emirates: Arabic</li>
    <li> :brazil: Portuguese</li>
    <li> :india: Hindi</li>
    <li> :de: German</li>
    <li> :tajikistan: Kurdish (Sorani)</li>
    <li> :tajikistan: Kurdish (Kurmanji)</li>
    <li> :netherlands: Dutch</li>
    <li> :it: Italian</li>
    <li> :iran: Persian</li>
    </ul>
    </li>
    <li>Greeting messages to users based on their activity if they haven't been active for more than a week or more than two weeks</li> 
    <li>Shows search history for each user through a scrollable inline list by pressing history button in the home keyboard</li>
    <li>Beautiful and vibrant user interface (messages and emojis)</li>
</ul>
<ul><li>
<h5>Playlists</h5><ol>
    <li>Users can have unlimited playlists and save unlimited audio files in each</li>
    <li>Users can edit playlist meta-data</li>
    <li>Users can edit saved audio files</li>
</ol>
</li></ul>
<img src="images/main_menu.PNG">
<caption align="center">Main menu screenshot</caption>
<br>
<li><h4>Admin features</h4></li>
<ul>
    <li>Real-time graph visualization (supports ArangoDB dashboard)</li>
    <li>Real-time indexed audio file visualization (supports Kibana dashboard)
    <br>
    * Kibana is a data visualization and exploration tool used for log and time-series analytics, application monitoring, and operational intelligence use cases. It offers powerful and easy-to-use features such as histograms, line graphs, pie charts, heat maps, and built-in geospatial support.
    </li>
</ul>
<li><h4>Other</h4></li>
<ul>
    <li>Extremely fast</li>
    <li>Documentation is provided in the codes (docstring)</li>
    <li>Handles database related exceptions</li>
    <li>Multi-threaded search (searches multiple requests asynchronously)</li>
    <li>Handles RTL texts perfectly</li>
</ul>
<ul>   
</ul>
</ol>

<hr class="dotted">

<div>
<div>
<h2 id="techstack">Technology stack</h2>
<p>Main tools & technologies used in developing TASE are as following:</p>
<ul>
<li>Elasticsearch &emsp; <img src="https://img.shields.io/badge/-Elasticsearch-005571?style=plastic&logo=elasticsearch">
<li>ArangoDB &emsp;&emsp;&ensp; <img src="https://img.shields.io/badge/ArangoDB-Database-green?style=flat-square&logo=arangodb&logoColor=white">
<li>Pyrogram &emsp;&emsp;&ensp;&ensp;<img src="https://img.shields.io/badge/Pyrogram-2CA5E0?style=plastic&logo=telegram&logoColor=white">
<li>Python get_text&ensp; <img src="https://img.shields.io/badge/Python-_Get_text_translations-3670A0?style=plastic&logo=python&logoColor=ffdd54">
<li>Celery &emsp;&emsp;&emsp;&emsp;&ensp;<img src="https://img.shields.io/badge/Celery-Task%20Queue-orange?logo=celery">
<li>RabbitMQ &emsp;&emsp;&emsp;<img src="https://img.shields.io/badge/RabbitMQ-Message%20Broker-red?logo=rabbitmq">
<li>Redis &emsp;&emsp;&emsp;&emsp;&ensp;<img src="https://img.shields.io/badge/Redis-Message%20Broker-red?logo=redis">
<li>Pydantic &emsp;&emsp;&emsp;&ensp;<img src="https://img.shields.io/badge/Pydantic-Data%20validation-yellowgreen">
<li>Jinja &emsp;&emsp;&emsp;&emsp;&emsp;<img src="https://img.shields.io/badge/Jinja-Templating%20engine-red?logo=jinja">

</ul>
</div>

<hr class="dotted">
<div id="contribution">
<h2>Call for Contributions</h2>
<p><b>We welcome your expertise and enthusiasm!</b></p>

<p>Ways to contribute to Telegram audio search engine:</p>
<ul>
  <li>Writing code</li>
  <li>Review pull requests</li>
  <li>Develop tutorials, presentations, documentation, and other educational materials</li>
  <li>Translate documentation and readme contents</li>
</ul>
<p>We love your contributions and do our best to provide you with mentorship and support. If you are looking for an 
issue to tackle, take a look at <a href="https://github.com/soran-ghaderi/tase/issues">issues</a>.</p>
</div>

<div>
  <h3>Issues</h3>
  <p>If you happened to encounter any issue in the codes, please report it
    <a href="https://github.com/soran-ghaderi/tase/issues">here</a>. 
    A better way is to fork the repository on <b>Github</b> and/or to create a pull request.</p>

</div>

<h3>Future work</h2>

- [ ] Voice search
- [ ] Add artist support
- [ ] 

<h2>If you found it helpful, please give us a <span>:star:</span></h2>
</div>
<hr class="dotted">
<div id="license">
<h2>License</h2>
<p><b>TASE is licensed under the Apache License, Version 2.0. See <a href="./LICENSE">LICENSE</a>  for the full license text.</b></p>
<div class="footer"> <pre>Copyright &copy; 2020-2022</pre>

<ul>
<li>
    <b>Soran Ghaderi</b> (soran.gdr.cs@gmail.com)<br>
    <ul>
        <li>Personal website: <a href="https://soran-ghaderi.github.io/">soran-ghaderi.github.io</a></li>
        <li>Linkedin: <a href="https://www.linkedin.com/in/soran-ghaderi/">Soran-Ghaderi</a></li>
        <li>Twitter: <a href="https://twitter.com/soranghadri">SoranGhadri</a></li>
    </ul>
</li>
<li>
    <b>Taleb Zarhesh</b> (taleb.zarhesh@gmail.com)<br>
    <ul>
        <li>Linkedin: <a href="https://www.linkedin.com/in/taleb-zarhesh/">Taleb Zarhesh</a></li>
        <li>Twitter: <a href="https://twitter.com/taleb__z">Taleb Zarhesh</a></li>
    </ul>
</li>
</ul>
</div> 
</div>
