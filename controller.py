import threading
import zlib
from zipfile import ZipFile

from DataObjects import AttackTargets, File

from unrar import rarfile


class Controller(object):
    def __init__(self, view):
        super().__init__()
        self.view = view

    def launch_attack(self, password_file, save_destination, hash_type, targets):
        attack_targets = AttackTargets()
        for target in targets:
            attack_targets.add_target(target)
        attack = DictionaryAttack(
                    self.view, password_file, save_destination, hash_type, attack_targets
                )
        attack.daemon = True
        attack.start()


class DictionaryAttack(threading.Thread):
    def __init__(self, view, password_file, save_destination, hash_type, targets):
        threading.Thread.__init__(self)
        # Thread attributes
        self.threadID = 1
        self.name = "AttackThread"

        self.view = view
        self.password_file = password_file
        self.save_destination = save_destination
        self.hash_type = hash_type
        self.attack_targets = targets
        self.supported_types = frozenset([".rar", ".zip"])

    def run(self):  # .start initiates this
        self.view.clear_text_output()  # clear the previous output if any
        self.view.insert_text_message(
            f"### INITIALISING ###",
            update_idle=True
        )
        targets = self.attack_targets.get_targets()
        for target in targets:
            if isinstance(target, File):
                self._attack_file(target)
            else:
                self._attack_folder(target)
        self.view.set_current_target("---------")
        self.view.insert_text_message(
            f"### PROGRAM END ###"
        )
        return None

    def _attack_folder(self, target_folder):
        self.view.insert_text_message(
            f"### TARGETING THE FOLDER {target_folder} ###"
        )
        self.view.set_current_target(target_folder)
        for file in target_folder.folder_files:
            self._attack_file(file)
        self.view.insert_text_message(
            f"### EXITING THE FOLDER {target_folder} ###"
        )

    def _attack_file(self, target_file):
        self.view.insert_text_message(
            f"## TARGETING THE FILE {target_file} ##"
        )
        self.view.set_current_target(target_file)

        is_supported_type = self._is_supported_file(target_file)
        if is_supported_type:
            pw_required = self._attempt_open_file(target_file)
            if pw_required:
                self.view.insert_text_message(
                    f"{target_file} is password protected."
                )
                self._crack_file(target_file)
            else:
                self.view.insert_text_message(
                    f"Ignore. {target_file} is not password protected.\n"
                )
        else:
            self.view.insert_text_message(
                f"Ignore {target_file}.\n{target_file.file_type} is not supported.\n"
            )

    def _is_supported_file(self, target):
        return (target.file_type in self.supported_types)

    def _attempt_open_file(self, target):
        path = target.file_path
        if target.file_type == ".rar":
            try:
                rf = rarfile.RarFile(path)
            except RuntimeError as err:
                if str(err).endswith("password required"):
                    return True
                else:
                    self.view.display_messagebox(err, "showerror")

        elif target.file_type == ".zip":
            try:
                zf = ZipFile(path).testzip()
            except RuntimeError as err:
                msg = "password required for extraction"
                if str(err).endswith(msg):
                    return True
                else:
                    self.view.display_messagebox(err, "showerror")

        return False  # if its not in protected types

    def _crack_file(self, target_file):
        self.view.insert_text_message(f"# ATTEMPTING TO CRACK {target_file} #")
        self.view.insert_text_message("_____", update_idle=True)
        found = False
        last_attempt = 0
        found_password = ""
        # dont use readlines as it will store the whole file in memory..
        # just read line by line
        pws = open(self.password_file, "r", encoding="latin1")
        for attempt, password in enumerate(pws, 1):
            password = password.strip()
            if target_file.file_type == ".rar":
                try:
                    # issue rarfile doesnt handle latin1 characters
                    # so use a different password file or amend the rockyouone
                    rar_obj = rarfile.RarFile(target_file.file_path, pwd=password)
                    found = True
                    found_password = password
                    last_attempt = attempt
                    rar_obj.extractall(self.save_destination)
                    break
                except RuntimeError as err:
                    if str(err).startswith("Bad password"):
                        update_idle = (attempt % 5 == 0)
                        self.view.insert_text_message(
                            f"Attempt {attempt}: '{password}' failed.",
                            update_idle=update_idle
                        )
                        if attempt % 250 == 0:
                            self.view.clear_text_output()
                        continue
                    else:
                        self.view.display_messagebox(err, "showerror")
                        break

            elif target_file.file_type == ".zip":
                try:
                    password_byte = bytes(password, "latin1")
                    ZipFile(target_file.file_path).extractall(path=self.save_destination,
                                                              pwd=password_byte)
                    found = True
                    found_password = password_byte.decode("latin1")
                    last_attempt = attempt
                    break
                except RuntimeError as err:
                    if str(err).startswith("Bad password"):
                        update_idle = (attempt % 5 == 0)
                        self.view.insert_text_message(
                            f"Attempt {attempt}: '{password}' failed.",
                            update_idle=update_idle
                        )
                        if attempt % 250 == 0:
                            self.view.clear_text_output()
                    else:
                        self.view.display_messagebox(err, "showerror")
                        break
                except zlib.error as zerr:
                    if str(zerr).startswith("Error -3"):
                        # If there are compression errors then skip
                        continue
                    else:
                        self.view.display_messagebox(zerr, "showerror")
                        break

        pws.close()
        if found:
            self.view.insert_text_message(
                f"Attempt {last_attempt}: '{found_password}'"
            )
            self.view.insert_text_message("Password Found")
            self.view.insert_text_message(
                f"The password [{found_password}] found after {last_attempt} attempts",
                update_idle=True
            )
            self.view.insert_text_message(
                f"{target_file} has been Cracked!!!"
            )
            self.view.insert_text_message(
                f"files extracted to {self.save_destination}",
                update_idle=True
            )
            self.view.insert_text_message(
                f"password will be saved to {self.save_destination}"
            )
            self.view.insert_text_message(f"________________")
            self._store_password(found_password, target_file.file_path)

        else:
            self.view.insert_text_message(
                f"Failed to Crack {target_file}",
                update_idle=True
            )

    def _store_password(self, password, target_path):
        line = f"{password} | {target_path}\n"
        dest = fr"{self.save_destination}\extracted_passwords.txt"
        f = open(dest, "a+")
        f.write(line)
        f.close()
        self.view.insert_text_message(
            f"Found password stored to {dest}"
        )
