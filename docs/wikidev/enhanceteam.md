Team collaboration is a recurring point in QualCoder. Although some possibilities exist, nothing is practical with the use of a server.
I've tried thinking about the question, and I propose an approach. Maybe not the best, but it could kick off the discussion:

The idea would be to create a "locks" lock file to indicate that a file is being edited (with a date to indicate the start: this could be a simple text file, or a JSON with date/coder). This lock would be reset (empty file) when no one is editing.
This would give:

- You enter a WebDAV server address into QualCoder (an open protocol for file synchronization)
- QualCoder checks whether there is a lock. If there is a lock, it indicates that someone is modifying, and that you must wait.
- If no lock, QualCoder creates / edits the lock file to indicate that someone is using it. The files are downloaded. You edit as usual.
- When done, you click a "send to server" button. The files are upload on server.
-  The lock is reset, indicating that the project is again available for modification.

It's maybe the 3e way to working with team, with Sequential Editing of the Same Project and Using a Master Project

An alternative is, at the time of the push, to merge the two .qda files (local and online) using the merge function, with the online version serving as the master document

Pb: lock file and sqlite don't comptatible with cloud.

Colin response:
We cannot do this first approach using the SQLite database. It needs to be a different database management system.
The advantages of using SQLite are:

    User-friendly: SQLite is ready for use. SQLite does not run as a server process, which means that it never needs to be stopped, started, or restarted and doesn’t come with any configuration files that need to be managed. These features help to streamline the path from installing SQLite to integrating it with an application.
    Portable: An entire SQLite database is stored in a single file. This file can be located anywhere in a directory hierarchy, and can be shared via removable media or file transfer protocol.

The above reasons are why I went with SQLite for the QualCoder project. Also, when beginning development - It is very easy to set up and very easy to transfer to another person. I was thinking at the time, it would be primarily for one or two people teams. This is typical for many university-based projects (Honours, Masters, PhD).

The downside is:
Limited concurrency: Although multiple processes can access and query an SQLite database at the same time, only one process can make changes to the database at any given time.

Kai did look at locks before, but this approach is risky.

One alternative would be to develop an alternative codebase around another DBMS such as MySQL or PostgreSQL

https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs-postgresql-a-comparison-of-relational-database-management-systems


Kai response:
It's not an easy thing to solve, for all the reasons Colin has mentioned already.
But I do think that the sequential editing approach suggested in the first post is a direction we could investigate further. If we had some kind of centralized server that would manage a lock on projects in use, this would prevent concurrent access and could work with SQLite. A locking mechanism would stop instances from accessing a project that is already opened by another team member, so QualCoder would remain a single-user app.
We would also need strict versioning of the project file (every change increases a counter in the main project db), which must also be stored on the central server. This way, any instance can ensure that it has the most recent project files before opening a project.
I'm not sure if WebDAV is the right protocol for managing the lock. A small dedicated QualCoder server, only used to manage project locks and versions in a database, could be a better approach. Each QualCoder project would get a unique GUID for identification, but the server would not know anything about the project's actual content.
People could then sync the actual project files using whichever service they have available - WedDAV, OneDrive, a university server... As discussed many times, the main project location should not be in a synced folder because this could interfere with SQLite. But we could automatically create a single zipped "transport file" when the project is closed and store this in a synced folder.
There are still plenty of problems to address, e.g., how to deal with stale locks if an instance crashes or loses network connection, or how to ensure that the synced project file is complete and not corrupted (we probably also need a hash stored on the server). But I think we should not abandon this idea too early, as improving the teamwork capabilities in QualCoder is something that users have requested many times already. However, this is definitely not something that could be implemented quickly, more of a long-term project.
What do you think?

Justin response:
Given that this issue is a recurring one, it’s worth giving it some serious thought. I’m not sure whether this thread is the most appropriate place… or whether a ‘dev’ page on the wiki would be better for noting down ideas and suggestions.

In my view, if a central server is to be set up, the solution must be lightweight and easy to deploy… Qualcoder is a lightweight piece of software used in many projects, not just at wealthy universities in the global North.

In my view, we must first look at how teamwork operates (teacher-student, groups of equal researchers, etc.), defining the practices and thus the architecture.

The project’s zip file is a separate issue, relating to the first and second aspects of teamwork, and must be considered independently.
