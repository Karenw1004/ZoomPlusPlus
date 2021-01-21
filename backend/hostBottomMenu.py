from time import sleep

class ZoomBottomMenu:
    def __init__(self, driver):
        self.driver = driver
        self.participants_open = False
        self.chat_open = False
        self.raised_hands_list = []

    def click_bottom_menu(self, ICON, is_open):
        supported_icons_dict = {
            "participants": "footer-button__participants-icon" ,
            "chat": "footer-button__chat-icon"
        }
        # The keys of the dictionary
        supported_icons = [*supported_icons_dict] 
        if ICON not in supported_icons:
            raise Exception("click_bottom_menu does not support this icon")

        found_icon = False
        class_name = supported_icons_dict[ICON]
        while (not found_icon):
            try:
                self.driver.find_element_by_class_name(class_name).click()
                found_icon = True
            except:
                sleep(1)
        is_open = not is_open
        print(f"Bottom menu {ICON} is {'open' if is_open else 'close'}")
        return is_open

    def get_participants_list(self):
        if not self.participants_open:
            self.participants_open = self.click_bottom_menu("participants", self.participants_open)
        
        participants_list = self.driver.find_elements_by_class_name("participants-item__display-name")
        name_without_bot = []
        for i in range(len(participants_list)):
            name = participants_list[i].get_attribute("innerHTML")
            if (name != "Zoom PlusPlus"):
                name_without_bot.append(name)
        print(f"Participants: {name_without_bot}\n") 
        
        # Close the participants menu
        self.participants_open = self.click_bottom_menu("participants", self.participants_open)
        return name_without_bot 

    # Will be able to bypass people whose name is (Host)
    def get_host_name(self):
        if not self.participants_open:
            self.participants_open = self.click_bottom_menu("participants", self.participants_open)
        x_path = "//span[@class='participants-item__name-label' and normalize-space()='Host' ]/parent::span/span[@class='participants-item__display-name']"
        host_element = self.driver.find_element_by_xpath(x_path)
        host_name = host_element.get_attribute("innerHTML")
        # Get the sibling element above host_element
        print(f"The host name is {host_name}")
        self.participants_open = self.click_bottom_menu("participants", self.participants_open)
        return host_name

    def get_current_reaction_list(self, reaction, curr_list):
        if not self.participants_open:
            self.participants_open = self.click_bottom_menu("participants", self.participants_open)
        reaction_dict = {
            "raise_hands": "participants-icon__participants-raisehand"
        }
        reaction_class_name = reaction_dict[reaction]
        reaction_list = self.driver.find_elements_by_class_name(reaction_class_name)
        self.reaction_count = len(reaction_list)
        print(f"Reaction count for {reaction} is {self.reaction_count}")

        for i in range(self.reaction_count):
            reaction_list[i] = reaction_list[i].find_element_by_xpath("../../..")
            reaction_list[i] = reaction_list[i].find_element_by_class_name("participants-item__display-name")
            name_of_participant_reacted = reaction_list[i].get_attribute("innerHTML")
            if name_of_participant_reacted not in curr_list:
                curr_list.append(name_of_participant_reacted)

        self.participants_open = self.click_bottom_menu("participants", self.participants_open)
        print(f"Reaction {reaction} list is {curr_list}")
        return curr_list

    def get_reaction_count(self,reaction):
        return self.reaction_count
    
    def get_next_person_with_reaction(self, reaction):
        self.raised_hands_list = self.get_current_reaction_list(reaction, self.raised_hands_list)
        if len(self.raised_hands_list) == 0:
            return None
        else:
            next_person_name = self.raised_hands_list.pop(0)
            return next_person_name

    # Assume that the chat is open 
    def choose_recipient(self, recipient_name): 
         
        found_recipient = False
        print("Finding chat recipient name....")
        while not found_recipient: 
            try: 
                chat_reciever_menu = self.driver.find_element_by_id("chatReceiverMenu").click() 
                found_recipient = True 
            except: 
                sleep(1) 
        print("Finish finding and clicked")
        # Wait for the recipient attendees to load 
        sleep(2) 
 
        # Finding the recipient name at the recipient attendes list 
        xpath = "//div[@class='scroll-content']"
        dropdown = self.driver.find_element_by_xpath(xpath) 
        xpath_string = "//child::a[contains(text(), '" + str(recipient_name) + "')]" 
        dropdown_element = dropdown.find_element_by_xpath(xpath_string) 
        dropdown_element.click() 
        return 
 
    def send_message(self, recipient_name, msg): 
        if not self.chat_open: 
            self.chat_open = self.click_bottom_menu("chat", self.chat_open) 
        self.choose_recipient(recipient_name) 
        # type message 
        chat_box = self.driver.find_element_by_class_name("chat-box__chat-textarea") 
        chat_box.send_keys(msg)
        chat_box.send_keys(u"\ue007")
        self.chat_open = self.click_bottom_menu("chat", self.chat_open) 
        return 
    
    def call_next_person(self,reaction):
        recipient_name = self.get_next_person_with_reaction(reaction)
        if recipient_name:
            self.send_message(recipient_name,"Your turn to ask question")
        else:
            print("None will be called next\n")
        return 