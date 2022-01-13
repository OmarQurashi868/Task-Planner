#### TaskPlanner

## Video Demo: https://youtu.be/Elsc46sUy6o

## Description:

Hello CS50, this is my submission for the final project. For this project I decided to go with a web application because I want to be a web developer one day. The project is called TaskPlanner, it's just a simple task planning board that helps you organize everything you need to do.

The main idea I had for TaskPlanner was to be able to have multiple boards, each with multiple lists for extra organization, and tasks inside those lists which you can freely delete and move freely between those lists (for example having a list for "To do" tasks and another one for "Done" and moving tasks to the second list once you're done with them. This is why whenever you create a board those 2 lists will be created automatically).

From the get-go, for some reason I just decided on the color blue for the website's theme. I had rough mouse sketches on what the UI of the main screen would like:

![Rough sketch of UI design](https://i.ibb.co/18ByNT0/ui-sketch.png)

I also had a diagram of the database and the connections and references between the different tables:

![Diagram of database structure](https://i.ibb.co/Xp29rpP/diagram.jpg)

As you can see in the diagram, the database had 4 tables, "users" for saving account data, "board" for storing the different boards and tie them to their respective accounts using the column "userid", "lists" for storing the different lists and tie them to the board in which they exist, and finally "tasks" which is also tied to "lists" in the same way.

First, I decided to work on *everything* around the main functionality but not the main functionality itself, so the main UI and other functions of the website (account system). I started by designing the login and registeration forms using Bootstrap, then I connected it to the database system using sqlite3. After that I set a placeholder for the index page and jumped straight to the account settings page (which lets you change your display name and your password). After a little bit of fiddling with widths for both PC and mobile it was time to go into the next part which was the navbar.

The nav bar was a completely new part to me but thankfully it didn't cause as many issues as I expected. Controlled from a button on the bar is also the side menu that lets you access the aforementioned account settings page and the logout function, but also the list of boards that in your account and the ability to manipulate them.

The newest and most troubling part was the main UI of the lists and tasks inside index, this is because I never worked with those card-like elements before. These cards brought out a lot of problems, especially for different viewport widths, a lot of random bugs were popping up everywhere. However due to immense help from the CS50 discord and a couple of friends we solved most (if not all) of those bugs.

In the end, I'd like the thank David J. Malan, Brian Yu and the entire CS50 team for this course and I'm really thankful for the knowledge presented in the course. I'd also like to thank the CS50 discord members and my friend who helped me overcome a lot of obstacles.