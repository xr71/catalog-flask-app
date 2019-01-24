# catalog-flask-app
Udacity Full Stack Developer - A Catalog application using Python Flask 

This is a back-end application that uses Vagrant, Python, Flask, Sqlalchemy, Sqlite, HTML, Bootstrap CSS, and Goolge OAuth Login. 

# To Run This Application
1. Install VirtualBox and Vagrant. Then clone the Udacity Fullstack VM Vagrantfile from here [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
2. Open the folder of the Udacity Vagrantfile repo and navigate to the directory containing the Vagranfile using your local terminal or Bash program, and then run `vagrant up`
3. Once the machine has been provisioned, clone this repository into the contents of the `catalog` directory on your local machine
4. Now enter `vagrant ssh` in your local machine's terminal and navigate to `/vagrant/catalog`
5. At this point, you can choose to run the application immediately by entering `python app.py` or run `python db_sim.py` to seed the database with some records first, and then proceed to run `python app.py`
6. Navigate to `localhost:8000` on your local machine's browser, and enjoy the Flask app. 

