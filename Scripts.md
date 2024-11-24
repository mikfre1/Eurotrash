# Group EuroTrash

## Introductions
> Your team name, and the names of all of your group members

EuroTrash<br>
Marlon, Mike, Max, and Henry


## Nested Model summary

![Nested Model visualization E01](nested_model.png)

Based on Tamara Munzer's Nested Model, our approach to this task is problem-driven work, starting from top.<br>
### Domain situation: user's need
Firstly, We focused on domain situation. The subject dataset is Eurovision Song contest voting dataset. It condtains contestants and voting records of this contest since 1956 involving multiple countries in Europe and others. By observing users, we found that the users are very engaged in this festival, and wants to both enjoy its history and music, but also explore and discover the correlations of the votes itself. In plain words, to "See the history of contest for fun, and wants to know how was the winners are picked."

### Data/Task absraction: What + Why
In the data and task absraction, we firstly reviewed 'What', the datasets. Both contestants and voting data is in form of table, mainly with categorical values like countries, and semi-final rounds, and quantative values like points, and ordered value like years, running on contest and places(ranking). <br>

Secondly the 'Why'. We turned the tasks from plain words into abstract form, and got 2 main user goals to enjoy the history and music, and another goal is to derive voting patterns behind the contest. And within these goals there are sub actions which are connected to our tasks of the visualization. <br>
> A reminder (or update) of your tool’s task list (0.5 points)

Please note that our tasks has been updated from our last report. We decided to focus more on deriving voting patterns.<br>
Intial 3 tasks are related to users enjoyment on history and music.
1) one is to 'Analyze' contest to 'discover' majoring winning country by 'exploring' through the years. user targets to discover outlying 'features'.
2) Second is also to 'Analyze' contest to 'discover' majoring theme of songs, by 'exploring' through the years. user targets to discover trends and outlying features.
3) Third is to 'Query' through countries places over the years and 'look up' to 'Compare' between 2 competing countries.

<br>
Latter 2 tasks are related to user goals to derive voting patterns.

4) Fourth task, is to 'discover' the voting pattern of countries by 'exploring' over the years. targeting to find trends in voting pattern.
5) Last task, to 'derive' the voting pattern based on current data. trying to find 'correlation' in voting countries.

### Visualization Encodings: How
> A demonstration of your tool’s functionalities, with voiceover description (2 points)<br>
> A clear characterization of the visual encoding, interactions, and view composition that your visualization(s) employ, with demonstration and voiceover description that clearly ties these decisions back to your project’s task, domain, and user characterization (5 points)

Now, in "HOW" stage, we designed encodings and interactions to fulfill these tasks.<br>
Here, I'll go on through our visualizations.
- Firstly our major interaction tool is to 'filter' data based on years in this slider. This 'changes' all our visualization accordingly.
- Now for the each visualization for each of our tasks.

    - First is geographical mapping of majoring countries. It maps colors to accumulated points per countries, let users to 'discover' the majoring countries. User can zoom in and out of the map, and detail on points is shown on 'selection'.
    - Second is word cloud of majoring theme. It 'maps' using the 'size' of words to its frequency in the lyrics. User can filter to show the themes of best or worst 5 ranked songs. By doing so, user can 'analyze' the majoring theme of the songs. Here, we used our first Algorithm based on llm model to tokenize and recognize positions in the lyrics. Considering the 'computational complexity', we decided to run through algorithm beforehand and store, then to load the operated data. Let users to quickly 'discover' majoring theme of songs.
    - Third is ranking comparison of 2 countries. we can select 2 countries from the list to manipulate this visualization. It encodes by alligning the historical places of 2 countries. And user can 'Query' and 'Compare' this result.

    Latter 2 visualizations are for users with detailed in voting behaviors and patterns. 

    - This is Voting matrix. This visulization shows the points given from one country to another country. We encoded the points given by countries in to color saturation, and aligned countries by the region. User can 'discover' the voting pattern of countries.
    - Last is Voting cluster. This visualization shows the correlation of countries votes on each others. The more they vote to others, the closer 2 dots are arranged. Here we used K means clustering Algorithm to show correlation. This algorithm can detect pattern and proximity and is fast enough to be rendered along with yearly filtering. Here, user can 'derive' the voting pattern based on current data.

    By Juxtaposing last 2 visualization, user can compare the regional voting patterns from matrix and newly derived voting pattern from clustering in a single view.



> A reflection on how well your interaction and encoding decisions support your tasks, with discussion on what you could refine to better support them (1.5 points)

Overall, our interaction and encodings in our visualization supports our tasks to enjoy the history of the contest and to derive voting patterns behind it.

For the next milestone, we can refine our visualization by using tele votes to deepen the analysis on voting habbits. or enrich interactions between visualization.

=================================================



### Video Response Instructions

Your video response should be an MP4 of no more than 4 minutes, and include an update on your VA tool’s
development progress:
• Your team name, and the names of all of your group members
• A Nested Model summary characterization of your project, as presented in lecture and exercise (1 point)
• A reminder (or update) of your tool’s task list (0.5 points)
• A demonstration of your tool’s functionalities, with voiceover description (2 points)
• A clear characterization of the visual encoding, interactions, and view composition that your visualization(s) employ, with demonstration and voiceover description that clearly ties these decisions back to your project’s task, domain, and user characterization (5 points)
•A reflection on how well your interaction and encoding decisions support your tasks, with discussion on what you could refine to better support them (1.5 points)


•Proper referencing of the sources used in your development, excluding IVDA lecture and exercise material