import datetime

# Global inventory list
inventory = []

# This is the "Confirm Retry" function which is to be used for when the system asks the user a yes or no question, particularly in "Register Item" and "Withdraw Item" section.
def confirm_retry(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ['y', 'n']:
            return answer == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")
        
# This is the "Main Menu" function, where the users are displayed a selection of functions that they can use in the inventory system.
def main_menu():
    while True:
        print("\n--- Restaurant Inventory System ---")
        print("1. Register Item")
        print("2. Check Inventory")
        print("3. Withdraw Item")
        print("4. Exit")
        choice = input("Enter choice (1-4): ")

        if choice == '1':
            register_item()
        elif choice == '2':
            check_inventory()
        elif choice == '3':
            withdraw_item()
        elif choice == '4':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# This is the "Register Item" function, where the users will be able to register or add items in the inventory.
def register_item():
    print("\n--- Register Item ---")
    print("Type 'exit' at any time to cancel and return to the main menu.")
    
    while True:
        item_name = input("Enter item name: ").strip()
        if item_name.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            return

        qty_input = input("Enter quantity: ").strip()
        if qty_input.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            return
        try:
            quantity = int(qty_input)
            if quantity <= 0: #Displays error message if the input is a negative integer, which is not accepted
                raise ValueError
        except ValueError:
            print("Invalid quantity. Must be a positive integer.")
            continue

        expiration_input = input("Enter expiration date (YYYY-MM-DD): ")
        if expiration_input.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            return
        entry_input = input("Enter entry date (YYYY-MM-DD): ")
        if entry_input.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            return
        
        try:
            expiration_date = datetime.datetime.strptime(expiration_input, "%Y-%m-%d").date()
            entry_date = datetime.datetime.strptime(entry_input, "%Y-%m-%d").date()
            if expiration_date < entry_date:
                print("Expiration date cannot be before entry date.")
                continue
        except ValueError:
            print("Invalid date format.")
            continue

        inventory.append({ #This records the user's input in the Inventory list
            "name": item_name,
            "quantity": quantity,
            "expiration": expiration_date,
            "entry": entry_date
        })

        print(f"{quantity} units of '{item_name}' added to inventory.")

        if not confirm_retry("Do you want to register another item? (y/n): "): 
            break

#This is the "Check Inventory" function, where users can view the list of items in the inventory as well as their information such as quantity, expiration dates, entry date, and status.
def check_inventory(): 
    print("\n--- Inventory Status ---")
    today = datetime.date.today()

    # Disposes expired items first, removing them in the inventory to avoid consumption or use of expired items
    expired_items = [item for item in inventory if item['expiration'] <= today]
    #This list comprehension creates a list of items whose expiration date is today or earlier—meaning they're expired. These items are stored in expired_items.
    inventory[:] = [item for item in inventory if item['expiration'] > today]
    #This modifies the inventory list in-place, keeping only the items that haven’t expired yet (expiration date is in the future).

    # Display current inventory list with status of the items
    if not inventory:
        print("No items in inventory.")
    else:
        print(f"{'Item':<20}{'Qty':<10}{'Entry Date':<15}{'Expiration':<15}{'Status'}") #This is for the table that will be displayed
        print("-" * 75)
        for item in inventory: #Assigns the status of different items based on how near their expiration date is
            days_left = (item['expiration'] - today).days
            if days_left > 7:
                status = "OK"
            elif 0 < days_left <= 7:
                status = "Nearly Expired"
            else:
                status = "Expired"
            print(f"{item['name']:<20}{item['quantity']:<10}{str(item['entry']):<15}{str(item['expiration']):<15}{status}") #This is for the table that will be displayed

    # Display disposed expired items with its information
    if expired_items:
        print("\nItems Disposed (Expired):")
        print(f"{'Item':<20}{'Qty':<10}{'Entry Date':<15}{'Expiration':<15}") #This is for the table that will be displayed
        print("-" * 65) 
        for item in expired_items:
            print(f"{item['name']:<20}{item['quantity']:<10}{str(item['entry']):<15}{str(item['expiration']):<15}") #This is for the table that will be displayed

#This is the "Withdraw Function" where the users can withdraw desired items from the inventory
def withdraw_item():
    print("\n--- Withdraw Item ---")
    print("Type 'exit' to cancel and return to the main menu.") 
    today = datetime.date.today()

    # Clean expired items first
    check_inventory()

    while True:
        item_name = input("\nEnter item name to withdraw: ").strip()
        if item_name.lower() == 'exit':
            return

        available_items = [item for item in inventory if item['name'].lower() == item_name.lower()] # This is for displaying items in a table
        if not available_items:
            print(f"No available stock for '{item_name}'.")
            if not confirm_retry("Do you want to try withdrawing another item? (y/n): "):
                return
            continue

        available_items.sort(key=lambda x: x['entry'])  # This is to perform the FIFO algorithm
        total_quantity = sum(item['quantity'] for item in available_items)
        print(f"Total available quantity for '{item_name}': {total_quantity}")

        valid_withdrawal = False  # 🔹 Flag to control valid withdrawal

        while True:
            withdraw_input = input("Enter quantity to withdraw: ").strip()
            if withdraw_input.lower() == 'exit':
                return
            try:
                withdraw_qty = int(withdraw_input)
                if withdraw_qty <= 0: # This is an error because the quantity input is a negative integer
                    raise ValueError
                if withdraw_qty > total_quantity: # This is an error because there are not enough stocks to be withdrawn
                    print("Error: Not enough quantity available.")
                    if not confirm_retry("Do you want to try withdrawing another item? (y/n): "):
                        return
                    break  # Break inner loop, continue outer loop
                valid_withdrawal = True
                break  # Valid input, proceed
            except ValueError:
                print("Invalid quantity. Must be a positive whole number.")
                if not confirm_retry("Do you want to try withdrawing another item? (y/n): "):
                    return
                break  # Break inner loop

        if not valid_withdrawal:
            continue  # Skip the withdrawal process

        print("\nWithdrawing:")
        remaining_to_withdraw = withdraw_qty
        details = []

        for item in available_items:
            if remaining_to_withdraw == 0: # This is when the items have no stock left
                break
            if item['quantity'] <= remaining_to_withdraw: # This is for updating the inventory list
                withdrawn = item['quantity']
                remaining_to_withdraw -= withdrawn
                inventory.remove(item)
            else:
                withdrawn = remaining_to_withdraw # This is for updating the inventory list
                item['quantity'] -= withdrawn
                remaining_to_withdraw = 0
            details.append((item['entry'], item['expiration'], withdrawn))

        print(f"Successfully withdrawn {withdraw_qty} units of '{item_name}'.") # This is the confirmation message of the withdrawal
        for d in details:
            print(f"- {d[2]} units (Entry: {d[0]}, Exp: {d[1]})") 

        if not confirm_retry("Do you want to withdraw another item? (y/n): "):
            break

# Run the system
if __name__ == "__main__":
    main_menu() 

# PS. In the "Register Item" page, you will notice that the entry date is manually entered instead of automatically by entering todays date, this is to test the functionality of the FIFO -
# - or First-in First-out algorithm by allowing the system to detect different dates, which can be sorted in the oldest to the most recent entry date, allowing FIFO to take place. Below is -
# the automatic entry date version of the "Register Item" for the recipients of this project to try. 

#def register_item():
    #print("\n--- Register Item ---")
    #print("Type 'exit' at any time to cancel and return to the main menu.")
    
    #while True:
        #item_name = input("Enter item name: ").strip()
        #if item_name.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            #return

        #qty_input = input("Enter quantity: ").strip()
        #if qty_input.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            #return
        #try:
            #quantity = int(qty_input)
            #if quantity <= 0:  #Displays error message if the input is a negative integer, which is not accepted
                #raise ValueError
        #except ValueError:
            #print("Invalid quantity. Must be a positive integer.")
            #continue

        #expiration_input = input("Enter expiration date (YYYY-MM-DD): ").strip()
        #if expiration_input.lower() == 'exit': #This allows the user to exit immediately without proceeding in this function if they'd wish to exit.
            #return
        
        #try:
            #expiration_date = datetime.datetime.strptime(expiration_input, "%Y-%m-%d").date()
            #entry_date = datetime.date.today()  # Automatically record today's date
            #if expiration_date < entry_date:
                #print("Expiration date cannot be before today's date.")
                #continue
        #except ValueError:
            #print("Invalid date format.")
            #continue

        #inventory.append({ #This records the user's input in the Inventory list
            #"name": item_name,
            #"quantity": quantity,
            #"expiration": expiration_date,
            #"entry": entry_date
        #})

        #print(f"{quantity} units of '{item_name}' added to inventory (Entry Date: {entry_date}).")

        #if not confirm_retry("Do you want to register another item? (y/n): "):
            #break