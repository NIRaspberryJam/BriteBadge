# BriteBadge
BriteBadge is a tool built in Python (3) that handles printing of name badges from Eventbrite attendee check-ins.   
The rough principle is based off [eventbadge](https://github.com/triblondon/eventbadge) which the Northern Ireland Raspberry Jam team had been using for a number of years.   

BriteBadge in comparison to eventbadge lacks any web interface, but is designed to run headless off a Raspberry Pi (using the brother_ql Python library).   
Like eventbadge, BriteBadge is designed to be used with a Brother QL-570 label printer. It is preconfigured to use 29mm x 90mm labels.      

### Setting up
1. Copy the `secrets/config_example.py` file to `secrets/config.py`.   
2. Edit the `secrets/config.py` file to add the Eventbrite event id, your eventbrite api key, a NIJIS day password (if using NIJIS, otherwise leave blank) and a delay between queries to Eventbrite.   
It is recommended to keep the delay at 4+ seconds.   
3. Install all the requirements of the project using `pip3 install -r requirements.txt`.   
4. Customise your label design (see below).   
5. To run the application, run with `main.ly` file with Python 3.   


### Rate limits   
It is worth keeping in mind that Eventbrite has API rate limits. The most recent rate limits can be found [here](https://www.eventbrite.com/platform/docs/rate-limits).   
BriteBadge queries Eventbrite every fixed amount of time, as defined in the delay configuration value, it is worth doing some quick maths to make sure you aren't going to hit the hourly/daily rate limits on the API.   

### Custom badge designs   
Tweaking the badge design isn't overly complicated. You need to edit the badge.py file in the `create_label_image` function.   
This is where the badge itself is built up, using PIL statements. These can be tweaked or changed as needed.   