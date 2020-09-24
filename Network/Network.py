"""
Network Device Class
"""
import sys
import traceback
from datetime import datetime
import time
import netmiko
import re
import json
import os
from pathlib import Path, PurePosixPath

VERBOSE = False

class NetworkDevice:
    """
    Network Device Class to be utilized in the Script
    """
    # Class instances

    def __init__(self, **kwargs):
        """
        Initial Setup information
        """
        self.hostname = ""
        self.host = kwargs["host"]
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.device_type = kwargs["device_type"]
        self.sheetname = kwargs["sheetname"]
        self.cmnt_msgs = []
        self.status = "Connection Not Started"
        self.connection = None
        self.model = ""
        self.boot_image = ""
        self.version = ""
        self.serial_number = ""
        self.cdp_neighbors = []
        self.lldp_neighbors = []
        self.connection = None

        self.start_connection()
        if self.is_connection_alive():
            self.__get_cdp_neigh()
            self.__get_lldp_neigh()
            self.end_connection()
        else:
            self.status = "Connection Error"

#######################################################
    def send_reload_in(self, reload_time=10):
        """Sends command reload in 20 (20 by default)"""
        if VERBOSE:
            print(self.host, "| sending reload in", reload_time)
        cmds = [['reload in {}'.format(reload_time), 'confirm'],
                ['y', '#']]
        self.send_cmd_with_prompt(cmds)


    def send_cmd_with_prompt(self, cmd_w_expected_str):
        """
        Sends commands with prompt, has to be a nested list of prompts, i.e.:
        [['reload in 10', 'Proceed with reload'], ['y', '#']]
        the first one is the command to send, second is the expected prompt value
        """
        output=""
        for cmd in cmd_w_expected_str:
            output += self.connection.send_command(
                command_string=cmd[0],
                expect_string=cmd[1],
                strip_prompt=False,
                strip_command=False
            )
        return output


    def is_connection_alive(self):
        """Returns Bool on connection alive or not"""
        if self.connection:
            # if self.connection.is_alive() and VERBOSE:
            #     print(self.host, "| Connection is active")
            # elif VERBOSE:
            #     print(self.host, "| Connection is not active")
            return self.connection.is_alive()
        else:
            return False


    def reestablish_connection(self, tries=3, wait_time=10):
        """
        Reestablishes the connection if connection is not active. By default it
        will attempt the connection 3 times, waiting 10 seconds between interval.
        """
        if not self.is_connection_alive():
            for i in range(tries):
                time.sleep(wait_time)
                self.start_connection_log()
                self.connection.establish_connection()
                if net_dev.is_connection_alive():
                    return
            if not net_dev.is_connection_alive():
                msg = "Issue with reestablishing connection to the device. Please attempt to access the device and correct issues or wait for the time reload."
                self.add_cmnt_msg(msg.format("UPLINK"), "Error")


    def start_connection(self):
        """
        Attempts to Connect to Device.
        ConnectionHandler variable. Will also submit "term len 0 " command.
        """
        try:
            if VERBOSE:
                print("{} | Starting Connection ".format( self.host))
            self.connection = netmiko.ConnectHandler(
                device_type=self.device_type+"_ssh",
                host=self.host,
                username=self.username,
                password = self.password,
                global_delay_factor=2
            )
            #self.start_connection_log()
            self.connection.enable()
            self.connection.send_command("term len 0")
            self.update_dev_info()
            self.status="Active"
            if VERBOSE:
                print("{} | Connection established, hostname is: {}".format(self.host, self.hostname))
        except Exception as e:
            print("{} | Connection Error with host, unable to connect. REASON:\n{}".format(self.host, e))
            self.add_detected_error(e)
            self.status = "Error"


    def update_dev_info(self):
        vers_info = self.send_command("show version")[0]
        self.hostname = vers_info["hostname"]
        if self.device_type=="cisco_ios":
            self.boot_image = vers_info["running_image"]
            self.model = vers_info["hardware"]
            self.version = vers_info["version"]
            self.serial_number = vers_info["serial"]
        elif self.device_type=="cisco_nxos":
            self.boot_image = vers_info["boot_image"]
            self.model = vers_info["platform"]
            self.version = vers_info["os"]
            self.serial_number = vers_info["serial_number"]


    def start_connection_log(self):
        """Starts logging in Append Mode"""
        log_path = Path("raw_logs/"+(self.host+"_raw_cli.log"))
        self.__add_time_stamp_to_file(log_path)
        self.connection.open_session_log(str(log_path), "append")
        if VERBOSE:
            print(self.host,"| Session Logging has been enabled")


    def send_command(self, command_string, use_textfsm=True):
        """
        sends_command via the connection and returns the output, if a template is
        specified then it uses textfsm with that particular template
        """
        return self.connection.send_command(command_string, use_textfsm=use_textfsm)


    def end_connection(self):
        """Ends Connection if it is alive"""
        if self.connection:
            if self.is_connection_alive():
                self.connection.disconnect()
                self.collection_time = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
                if self.status == "Active":
                    self.status = "Complete"
                if VERBOSE:
                    print("{} | Ending Connection".format( str(self.host)))


    def save_config(self):
        """Sends 'wr mem' to the connection to save the current running config"""
        if VERBOSE:
            print(self.host, "| Saving running configuration to startup config with 'wr mem' command")
        self.connection.save_config()
###############################################################################
    def __add_time_stamp_to_file(self, file_path):
        """Adds a timestamp as an append to a file"""
        f = open(file_path, "a+")
        f.write("\n"+"#"*80+"\n")
        f.write(" "*30+self.__time_stamp(":")+" "*30)
        f.write("\n"+"#"*80+"\n")
        f.close()


    def __time_stamp(self, out_type="L"):
        """return the current time"""
        if out_type=="L":
            return datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        elif out_type==":":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def get_vers_info(self):
        """
        Reads the "show version" information and updates the NetworkDevice
        Variables accordingly.
        """
        tmpl = "cisco_ios_show_version.textfsm"
        cmd = "show version"
        self.show_output_json[cmd] = self.send_command(cmd, tmpl)
        output = self.show_output_json[cmd][0]
        trantab = str.maketrans("", "", "\'\"{}[]")
        self.model = str(output["hardware"]).translate(trantab)
        self.version = output["version"]
        self.serial_num = str(output["serial"]).translate(trantab)


    def verify_cdp_neigh(self, **kwargs):
        matching_neighbors = self.find_neighbor(kwargs["neighbor"], "cdp")
        for intf in matching_neighbors:
            if intf["local_short_if"] == get_short_if_name(kwargs["local_interface"]).lower():
                if intf["remote_short_if"] == get_short_if_name(kwargs["remote_interface"]).lower():
                    return "Verified via CDP"
        return None


    def verify_lldp_neigh(self, **kwargs):
        matching_neighbors = self.find_neighbor(kwargs["neighbor"], "lldp")
        for intf in matching_neighbors:
            if intf["local_short_if"] == get_short_if_name(kwargs["local_interface"]).lower():
                if intf["remote_short_if"] == get_short_if_name(kwargs["remote_interface"]).lower():
                    return "Verified via LLDP"
        return None


    def __get_cdp_neigh(self):
        """Gets the CDP Neighbors"""
        if VERBOSE:
            print(self.host, "| Getting CDP neighbors")
        self.cdp_neighbors = self.send_command("show cdp neigh detail")
        for neigh in self.cdp_neighbors:
            neigh["mod_host"]=neigh["destination_host"].split(".")[0]
            neigh["remote_short_if"] = get_short_if_name(neigh["remote_interface"]).lower()
            neigh["local_short_if"] = get_short_if_name(neigh["local_interface"]).lower()


    def __get_lldp_neigh(self):
        """Gets the LLDP Neighbors"""
        if VERBOSE:
            print(self.host, "| Getting LLDP neighbors")
        self.lldp_neighbors = self.send_command("show lldp neigh detail")
        for neigh in self.lldp_neighbors:
            neigh["mod_host"]=neigh["neighbor"].split(".")[0]
            neigh["remote_short_if"] = get_short_if_name(neigh["remote_interface"]).lower()
            neigh["local_short_if"] = get_short_if_name(neigh["local_interface"]).lower()



    def add_cmnt_msg(self, msg, type):
        """Adds commments that will be added to sheet"""
        comment = str(len(self.cmnt_msgs)+1)+" | "
        comment += str(msg)
        t_time = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        self.cmnt_msgs.append([comment, t_time, type])


    def add_detected_error(self,e):
        """Adds a detected Exception Error to the comment messages as an Error"""
        exc_tb = sys.exc_info()[2]
        exc_type = sys.exc_info()[0]
        exc_line = exc_tb.tb_lineno
        f_name = traceback.extract_tb(exc_tb,1)[0][2]
        t_err_msg = "{} | Exception Type: {} | At Function: {} | Line No: {} | Error Message: {}"
        t_err_msg = t_err_msg.format(self.host, exc_type, f_name, exc_line, e)
        self.add_cmnt_msg(t_err_msg, "Error")


    def get_etherch_intf(self, eth_ch_gr, downlink_or_uplink):
        """runs the Methods to get eth_ch information"""
        if downlink_or_uplink == "downlink":
            eth_ch_list = self.downlink_ether_ch
        elif downlink_or_uplink == "uplink":
            eth_ch_list = self.uplink_ether_ch
        for eth_info in eth_ch_list:
            if eth_info["group"] == eth_ch_gr:
                return eth_info["interfaces"]


    def find_neighbor(self,neigh_name, cdp_lldp):
        """Looks for all CDP Neighbors that match the destination host name"""
        if cdp_lldp=="cdp":
            return list(filter(lambda net_dev_neigh: net_dev_neigh["mod_host"].lower() == neigh_name.lower(), self.cdp_neighbors))
        elif cdp_lldp=="lldp":
            return list(filter(lambda net_dev_neigh: net_dev_neigh["mod_host"].lower() == neigh_name.lower(), self.lldp_neighbors))


    def is_supported(self):
        """Checks if a device is supported based on list in Excel sheet"""
        supported = False
        if VERBOSE:
            print(self.host, "| Checking if it is supported")
        # Look by Model
        if "ASR" in self.model:
            found_list = list(filter(lambda dev: dev["model"] == self.model, self.supported_devices))
        else:
            found_list = list(filter(lambda dev: dev["model"] in self.model, self.supported_devices))
        # if not found then model not supported
        if not found_list:
            self.__not_supported("Model")
            return supported
        # Else continue, and look for the Version
        else:
            for supported_model in found_list:
                if supported_model["version"] == self.version:
                    supported = True
                    if VERBOSE:
                        print(self.host,"| Device is supported")
        # if supported not True, it means version was not found
        if not supported:
            self.__not_supported("Version")
        return supported


    def backup_config_to_text(self):
        """Saves a configuration directly to a textfile, will generate in a subfolder """
        if VERBOSE:
            print(self.host, "| Saving a copy of the running configuration to a text file")
        run_config = self.connection.send_command("show run", delay_factor=5)
        fname = self.host+"_"+self.hostname+"_"
        fname += datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")+"_run_conf.cfg"
        fname = self.out_dir_path/"backup_configs"/fname
        with open(fname, 'w+') as filehandle:
            filehandle.write(run_config)


def get_short_if_name(interface, device_type = "cisco_ios"):
    """
    Returns short if name. for cisco_ios it returns first 2 char and the
    interface number. Everything else it returns the first 3 plus number.
    """
    number = re.compile(r"(\d.*)$")
    name = re.compile("([a-zA-Z]+)")
    number = number.search(interface).group(1)
    name = name.search(interface).group(1)
    short_name = ""
    if device_type == "cisco_ios":
        short_name = left(name, 2)
    elif device_type in ["cisco_nxos", "cisco_xr"]:
        port = left(name, 3).lower()
        if port == "eth":
            short_name = left(name, 3)
        elif port == "vla":
            short_name = left(name, 4)
        elif port == "mgm":
            short_name = left(name, 4)
        else:
            short_name = left(name, 2)
    if int(left(number, 1)) >= 0 or number is None:
        short_name = short_name + str(number)
    return short_name


def left(s, amount):
    """Returns the left characters of amount size"""
    return s[:amount]
