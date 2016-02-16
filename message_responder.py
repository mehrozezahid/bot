import re
import httplib2
import json

INCORRECT_MENTION_NAME = "No user with that mention name. Did you make a typo?"
NO_MENTION_NAME = "You forgot to mention who you're giving feedback to! " \
                  "Type the mention name of the user after 'kudos' starting with '@"
NO_FEEDBACK_TEXT = "You forgot to include some feedback text!"
INCORRECT_PRIVACY_SETTING = "You chose an incorrect privacy setting. Choose from " \
                            "public, private or anonymous."
SELF_ANONYMOUS_FEEDBACK = "You can't give anonymous feedback to yourself (doh)" \
                          " Choose a different privacy setting"


class ChatBot():
    VALID = (
        # (command name, callback, command helpline)
        # (r"\s*teams\s*", "list_clients",
        #  "teams - show a list of teams"),
        #
        # (r"\s*which\s*project\s*$", "which_project",
        #  "which project - show the name of the project you are working on"),
        # # (r"\s*projects\s*$", "list_projects", "projects - shows a list of all projects"),
        #
        # (r"\s*projects\s+[\w]+$", "list_projects",
        #  "projects <team_name> - show all projects for given team"
        #  " e.g. projects kayak"),
        #
        # (r"\s*start\s+[\w]+-[\w]+(\s+'(?:''|[^']*)*')?\s*$", "start_project",
        #  "start <team_name>-<project_name> <task> - start work on a project"
        #  " e.g. start kayak-moboqa 'New test plan'"),
        #
        # (r"\s*stop(\s+[\w]+-[\w]+)?\s*$", "stop_project",
        #  "stop - stop work on a project"),
        #
        # (r"\s*add\s+[\w]+\s*$", "add_client",
        #  "add <team_name> - add a new team"
        #  " e.g. add kayak"),
        #
        # (r"\s*add\s+[\w]+\s+[\w]+\s*$", "add_project",
        #  "add <team_name> <project_name> - add a new project for given team"
        #  " e.g. add kayak moboqa"),
        #
        # (r"\s*team\s+[\w]+-[\w]+\s*$", "team",
        #  "team <team_name>-<project_name> - show a list of all people working on given project"),
        #
        # (r"\s*team\s+[\w]+\s*$", "team_members",
        #  "team <team_name> - show a list of all people working on given team"),

        # --------------------------------------------------------------------------------------------------------------

        (r"\s*kudos\s*\w*", "send_kudos",
         "kudos <privacy> <mention_name> <feedback_text> - "
         "congratulate a person on a job well done", "public"),

        (r"\s*suggestion\s*\w*", "suggestion",
         "suggestion <privacy> <mention_name> <feedback_text> - "
         "let a person know how something could have been even better",
         "private"),

        (r"\s*help\s*$", "help", "help - show a list of valid commands", ""),

        (r".+", "default", "", ""),
    )

    def handle_message(self, msg, args):
        print("In Chatbot_handle_message")
        for pattern in self.VALID:
            match = re.match(pattern[0], msg, re.IGNORECASE | re.DOTALL)
            if match:
                to_call = getattr(self, pattern[1].lower())
                return to_call(msg, args, pattern).rstrip()

    def send_kudos(self, msg, args, pattern):
        print("In Chatbot_send_kudos")
        feedback_type = "kudos"
        # feedback_parameters = re.match(r"kudos\s+(\w*)\s*@+([^\s+]+)\s+(.*)", msg, re.IGNORECASE)
        # feedback_parameters = re.match(r"kudos\s+(\w*)\s*(@*)([^\s+]+)\s+(.*)", msg, re.IGNORECASE)

        # privacy, target_user, feedback_text = self.parse_message(msg, feedback_parameters, pattern[3])

        if re.match(r"kudos\s+(public |private |anonymous ){0,1}\s*([\w\-][\w\-\.]+@[\w\-][\w\-]+\.[a-zA-Z]+)+(\s+.*)*",
                    msg, re.IGNORECASE):
            feedback_parameters = re.match(
                r"kudos\s+(public |private |anonymous ){0,1}\s*([\w\-][\w\-\.]+@[\w\-][\w\-]+\.[a-zA-Z]+)+(\s+.*)*",
                msg, re.IGNORECASE)
        else:
            check = re.search(r"([\w\-][\w\-\.]+@[\w\-][\w\-]+\.[a-zA-Z]+)+", msg, re.IGNORECASE)
            try:
                check.group(1)
                return "Incorrect command. The format is:\n" + pattern[2]
            except:
                return "Not a valid email! Did you make a typo?"

        privacy, target_user, feedback_text = self.parse_message(msg, feedback_parameters, pattern[3])

        if target_user in [INCORRECT_MENTION_NAME, NO_MENTION_NAME]:
            return target_user

        if privacy == INCORRECT_PRIVACY_SETTING:
            return INCORRECT_PRIVACY_SETTING

        if not feedback_text:
            return NO_FEEDBACK_TEXT

        if args['user']['email'] == target_user and privacy == 'anonymous':
            return SELF_ANONYMOUS_FEEDBACK

        return "type: " + feedback_type + "\nfrom: " + args['user'][
            'email'] + "\nto: " + target_user + "\nprivacy: " + privacy + "\ntext: " + feedback_text

    def suggestion(self, msg, args, pattern):
        print("In Chatbot_suggestion")
        feedback_type = "suggestion"
        # feedback_parameters = re.match(r"kudos\s+(\w*)\s*@+([^\s+]+)\s+(.*)", msg, re.IGNORECASE)
        # feedback_parameters = re.match(r"kudos\s+(\w*)\s*(@*)([^\s+]+)\s+(.*)", msg, re.IGNORECASE)

        # privacy, target_user, feedback_text = self.parse_message(msg, feedback_parameters, pattern[3])

        if re.match(r"suggestion\s+(public |private |anonymous ){0,1}\s*([\w\-][\w\-\.]+@[\w\-][\w\-]+\.[a-zA-Z]+)+(\s+.*)*",
                    msg, re.IGNORECASE):
            feedback_parameters = re.match(
                r"suggestion\s+(public |private |anonymous ){0,1}\s*([\w\-][\w\-\.]+@[\w\-][\w\-]+\.[a-zA-Z]+)+(\s+.*)*",
                msg, re.IGNORECASE)
        else:
            check = re.search(r"([\w\-][\w\-\.]+@[\w\-][\w\-]+\.[a-zA-Z]+)+", msg, re.IGNORECASE)
            try:
                check.group(1)
                return "Incorrect command. The format is:\n" + pattern[2]
            except:
                return "Not a valid email! Did you make a typo?"

        privacy, target_user, feedback_text = self.parse_message(msg, feedback_parameters, pattern[3])

        if target_user in [INCORRECT_MENTION_NAME, NO_MENTION_NAME]:
            return target_user

        if privacy == INCORRECT_PRIVACY_SETTING:
            return INCORRECT_PRIVACY_SETTING

        if not feedback_text:
            return NO_FEEDBACK_TEXT

        if args['user']['email'] == target_user and privacy == 'anonymous':
            return SELF_ANONYMOUS_FEEDBACK

        return "type: " + feedback_type + "\nfrom: " + args['user'][
            'email'] + "\nto: " + target_user + "\nprivacy: " + privacy + "\ntext: " + feedback_text

    def parse_message(self, msg, feedback_parameters, default_privacy_type):
        # privacy = self.get_privacy(feedback_parameters)
        # if not privacy:
        #     privacy = default_privacy_type
        #
        # if feedback_parameters.group(2) and feedback_parameters.group(3).lower():
        #     mention_name = feedback_parameters.group(3)
        #     target_user = self.get_target_user(mention_name)
        # else:
        #     target_user = NO_MENTION_NAME
        #
        # if feedback_parameters
        #
        # if feedback_parameters.group(4):
        #     feedback_text = feedback_parameters.group(4)
        # else:
        #     feedback_text = None

        try:
            privacy = feedback_parameters.group(1).lower().strip()
        except:
            privacy = default_privacy_type

        target_user = feedback_parameters.group(2)

        try:
            feedback_text = feedback_parameters.group(3).strip()
        except:
            feedback_text = None

        return privacy, target_user, feedback_text

    # def get_target_user(self, mention_name):
    #     """
    #     API call to HipChat to retrieve user email
    #     :param mention_name: HipChat mention name of the target user of the feedback
    #     :return: Email of user from HipChat API or "User doesn't exist" message
    #     """
    #     resp, content = httplib2.Http().request("%s?format=json&auth_token=%s" %
    #                                             ("https://api.hipchat.com/v2/user/@" + mention_name,
    #                                              "vwTlL3hAO7a4XH2TqsP991KAF0C2MYvFf0ovmlbE"))
    #     if resp['status'] == "404":
    #         return INCORRECT_MENTION_NAME
    #     return json.loads(content)['email']

    def get_privacy(self, feedback_parameters):
        if feedback_parameters.group(1).lower() in ['private', 'public', 'anonymous']:
            return feedback_parameters.group(1).lower()
        elif feedback_parameters.group(1):
            return INCORRECT_PRIVACY_SETTING
        else:
            return None

    def help(self, msg, args, pattern):
        response = "Valid commands:\n"
        for v in self.VALID:
            response += v[2] + "\n"
        return response

    def default(self, msg, args, pattern):
        response = "Command not found: '%s'. " \
                   "Type 'help' for a list of valid commands" % msg
        return response
