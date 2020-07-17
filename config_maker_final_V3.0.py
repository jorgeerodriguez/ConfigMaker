import csv
import logging
logging.raiseExceptions = False

try:
    # importing packages required for the script
    from netmiko import ConnectHandler
    import paramiko
    from datetime import datetime
    import datetime
except:

    print("Packages not installed. Please import packages paramiko and datetime using PIP installer")

    # opening ip.txt file
    # the ip.txt has entries of ip and hostname in format ip:hostname
now1 = datetime.datetime.now()
today1 = str(now1.year) + '-' + str(now1.month) + '-' + str(now1.day) + \
    '-' + str(now1.hour) + '-'+str(now1.minute) + \
    '-'+str(now1.second)

log_file = 'log'+'-'+today1+'.csv'
file_log = open(log_file, 'a+')


def fetch_value():
    try:
        print()
       # print("Opening file ip.txt")
        file_ip = open('ip.txt', "r")
        print("ip.txt is open now")
    except:
        print("Error occured while opening the ip.txt in read mode")
        file_ip = fp = open('ip.txt', "w+")
        print("Ip.txt is created . Please enter the ip and hostname in ip:hostname format in every new line")
        fp.close()
        exit()
    dictionary_of_ip_hostname = {}
    dictionary_of_variable_file = {}

    try:

        for line_ip_file in file_ip:
            fields_in_ip_file = line_ip_file.split(":")
            ip = fields_in_ip_file[0]
            hostname = fields_in_ip_file[1].strip()
            dictionary_of_ip_hostname[ip] = hostname

        print("IP and Hostname is separated")
    except Exception as e5:
        print("Error occured while ip and hostname finding")
    finally:
        # print("ip.txt is closing now")
        file_ip.close()
        if file_ip.closed:
            print("ip.txt is closed\n")
    print()
    print("-" * 100)
    print()
    print()

    # code to retrieve sername ,password , auth_pass from variables.txt
    try:
        # print("Opening variable.txt file")
        file_variables = open('variables.txt', "r")
        print("variable.txt is open now")
    except:
        print("The variables file does not exist")
        file_variables = fp = open('variables.txt', "w+")
        print("The file variable.txt is created . Please enter the username ,password , auth_pass")
        print("The format is :")
        print("username:enter the user name")
        print("password:enter the password")
        print("auth:password")
        fp.close()
        exit()
    try:
        for line_in_variable_file in file_variables:
            fields_in_variable = line_in_variable_file.split(":")
            dict_key = fields_in_variable[0]
            dict_value = fields_in_variable[1].strip()
            dictionary_of_variable_file[dict_key] = dict_value
        print("Username, password and auth_password is retrieved")
    except:
        print("Error occured while retrieving username or password or auth_pass ")

    finally:
        # print("variables.txt is closing now")
        file_variables.close()
        print("variables.txt is closed \n")

    print()
    print("-" * 100)
    print()
    # calling function to configure
    configure(dictionary_of_ip_hostname, dictionary_of_variable_file)
    return


def configure(dictionary_of_ip_hostname, dictionary_of_variable_file):
    result = True
    global file_log
    try:
        list_of_wrong_hostname = []
        server_username = dictionary_of_variable_file['username'].strip()
        server_password = dictionary_of_variable_file['password'].strip()
        for key, val in dictionary_of_ip_hostname.items():
            obj = connect_host(key, 22, server_username, server_password)
            if 'connection timed out' not in str(obj):
                print("Connection established with " + str(key))
            else:
                print("Connection failed with " + str(key))
            if obj is not None:
                result = push_config(obj, key, val)
                obj.disconnect()
                print("Connection with " + str(key)+" ended\n")
                print("-"*100)
                print()
            if result == False:
                list_of_wrong_hostname.append(str(key))
        if len(list_of_wrong_hostname) > 0:
            print("The wrong hostname entered in ip.txt are :")
            print(list_of_wrong_hostname)
        file_log.close()
    except Exception as e4:
        print(e4)


def connect_host(key, sshport, server_username, server_password):
    try:
        print(key)
        cisco = {
            'device_type': 'cisco_ios',
            'host': key,
            'username': server_username,
            'password': server_password,
            'port': sshport,
            'secret': 'secret',
        }
        # print("check")
        cis_con = ConnectHandler(**cisco)
        # the cis_con is the object which contain the connection returned by connecthandler after connecting.
        # print(cis_con)
        cis_con.enable()
        prompt = cis_con.find_prompt()
        print(prompt)
        if len(prompt) > 0:
            print("Authentication successfull with "+str(key))
            return cis_con
    except Exception as e5:
        print("Authentication is not successful.Error in connect_host. Please try again")
        print(e5)


def push_config(obj, key, val):
    global today1
    error = "False"
    # enable2
    obj.enable()
    hostname_output = str(obj.send_command(
        "Show running-config | i hostname")).split(" ")[1]
    test_result = str(hostname_output) == str(val)

    try:
        if test_result:
            print("Hostname matches\n")
            # config_before = obj.send_command("Show running-config")
            date = str(now1.year) + '-' + str(now1.month) + '-' + str(now1.day)
            time = str(now1.hour) + '-'+str(now1.minute)+'-'+str(now1.second)
            filename_pre = key + '-' + today1 + '-preConfig.txt'
            try:
                pre_conf_file = open("preconfig.txt", "r")
               # commands_pre = pre_conf_file.read()
            except:
                print("preconfig.txt not present. Please save a file preconfig.txt in the current directory with the pre config commands ")
                exit()

            # print(commands_pre)
            file_date_pre = open(str(filename_pre), "w+")
            for commands_pre in pre_conf_file:
                config_before = str(obj.send_command(str(commands_pre)))
                file_date_pre.write(commands_pre)
                file_date_pre.write("\n")
                file_date_pre.write(config_before)
                file_date_pre.write(
                    "\n-----------------------------------------------------------------------------------------------------------------\n")
           # print(config_before)
            print()
            print("Taking backup before configuration update")
            print(filename_pre)
            print()
           # file_date_pre = open(str(filename_pre), "w+")
            # file_date_pre.write(config_before)
            file_date_pre.close()
            pre_conf_file.close()
            command_logs = {}
            try:
                file_config = open("config.txt", "r")
                commands = file_config.readlines()
            except:
                print(
                    "config.txt not present. Please save a file config.txt in the current directory with the configurations ")
                exit()
            for i in commands:
                command_logs[i.strip("\n")] = "Success"
            errs = ["% Invalid", "% Ambiguous", "% Incomplete"]
            print("Configuration update in progress")
            print()
            configurations_command = obj.send_config_set(commands)
            # print(configurations_command)
            exec_log = today1 + '-executionLogs.txt'
            execution_logs = open(str(exec_log), "a")
            writing_string = "Execution logs for " + str(key)
            execution_logs.write(configurations_command)
            execution_logs.write(
                "\n---------------------------------------------------------------------------------------------------------------------------\n")
            execution_logs.close()
            print("\nExecution logs saved as " + exec_log)
            print()
            error_exists = [i for i in errs if i in configurations_command]
            errcmd = []
            if error_exists:
                row_err = configurations_command.split("%")
                for i in row_err[:-1]:
                    err = i.split("#")[-1]
                    filtered_err = err.split("^")[0].strip()
                    errcmd.append(filtered_err)
            for i in errcmd:
                command_logs[i.strip("#")] = "Failed"
            try:
                global file_log
                global log_file
                for key2, val2 in command_logs.items():
                   # print([str(date), str(time), val, val2, key2])
                    csv_write = [str(date), str(time), val, val2, key2]
                    file_writer = csv.writer(file_log)
                    file_writer.writerow(csv_write)
            except Exception as e2:
                print("Error while writing logs " + e2)
            print("Status of command execution entries done in log.csv\n")
            file_config.close()
            # config_after = obj.send_command("Show running-config")
            try:
                post_conf_file = open("postconfig.txt", "r")
               # commands_post = post_conf_file.readlines()
            except:
                print("postconfig.txt not present. Please save a file postconfig.txt in the current directory with the pre config commands ")
                exit()

           # config_after = str(obj.send_command(str(commands_post)))

            filename_post = key + '-' + today1 + '-postConfig.txt'
            print("Taking backup after configuration update")
            print(filename_post)
            print()

            file_date_post = open(str(filename_post), "w+")
            for commands_post in post_conf_file:
                config_after = str(obj.send_command(str(commands_post)))
                file_date_post.write(commands_post)
                file_date_post.write("\n")
                file_date_post.write(config_after)
                file_date_post.write(
                    "\n-----------------------------------------------------------------------------------------------------------------\n")
            file_date_post.close()
            post_conf_file.close()

            return True

        else:
            print("The hostname is wrong for the ip " + key)
            print("Please correct the ip.txt file for the above above")
            return False
    except Exception as e1:
        print("Error occured while deploying configuration:" + e1)


fetch_value()
print()
print("SCRIPT EXECUTED.")
# def main():
# calling fetch_value to retrieve values from files
# print("Calling fetch func\n")
# fetch_value()


# if __name__ == "__main__":
# main()
