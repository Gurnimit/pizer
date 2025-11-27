#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os, time
import concurrent.futures
import itertools
import threading
try:
    import pyzipper as zipfile
except ImportError:
    import zipfile
sys.dont_write_bytecode = True

from .Core.Stylesheet.Styling import sd, bc
from .Core.Console import Console
from .Core.Commands import Command
from .Core.Validity import Validation
from .brute_force import BruteForceGenerator

class ZipRip:
    def __init__(self):
        self.Console = Console()
        self.Cmd = Command()
        self.Validator = Validation()

        self.Wordlist = ""
        self.ZipFile = ""
        self.ExtractToPath = ""
        self.Passwords = [] # Can be a list or a generator
        
        self.AttackMode = "dictionary" # dictionary or bruteforce
        self.BruteForceConfig = {
            "max_length": 4,
            "use_lower": True,
            "use_upper": True,
            "use_digits": True,
            "use_symbols": False
        }

        self.Tries = 0
        self.FoundPassword = None
        self.ResponseData = []
        self.StopEvent = False
        
        # Thread-local storage for ZipFile handles
        self.thread_local = threading.local()

    def SetWordlist(self):
        if self.Wordlist:
            Wordlist = self.Wordlist
        else:
            Wordlist = str(input(f"{bc.BC} Password Wordlist: {bc.GC}"))

        if (not self.Validator.NotEmpty(Wordlist)):
            if self.AttackMode == "dictionary":
                self.Cmd.Clear(f"{sd.eBan}{bc.BC} Password wordlist is required\n", True)

        elif (not os.path.isfile(Wordlist)):
            self.Cmd.Clear(f"{sd.eBan}{bc.BC} No wordlist named {bc.RC}{Wordlist}{bc.BC} exists\n", True)

        self.Wordlist = Wordlist

    def SetZipFile(self):
        if self.ZipFile:
            ZipFile = self.ZipFile
        else:
            ZipFile = str(input(f"{bc.BC} Zip File: {bc.GC}"))

        if(not self.Validator.NotEmpty(ZipFile)):
            self.Cmd.Clear(f"{sd.eBan}{bc.BC} Zip File is required\n", True)

        elif (not ZipFile.endswith(".zip")):
            self.Cmd.Clear(f"{sd.eBan}{bc.BC} file {bc.RC}{ZipFile}{bc.BC} is not a .zip file", True)

        elif (not os.path.isfile(ZipFile)):
            self.Cmd.Clear(f"{sd.eBan}{bc.BC} no zip file named {bc.RC}{ZipFile}{bc.BC} exists\n", True)

        self.ZipFile = ZipFile

    def SetZipFileDirectory(self):
        if (not self.Validator.NotEmpty(self.ZipFile)):
            self.Cmd.Clear(f"{sd.eBan}{bc.BC} could not establish zip file directory", True)

        # Extract to the same directory as the zip file
        ZipDirectory = os.path.dirname(os.path.abspath(self.ZipFile))
        ZipName = os.path.splitext(os.path.basename(self.ZipFile))[0]
        self.ExtractToPath = os.path.join(ZipDirectory, ZipName)

    def SetPasswords(self):
        if self.AttackMode == "dictionary":
            try:
                with open(self.Wordlist, "rb") as PasswordWordlist:
                    self.Passwords = (Line.strip() for Line in PasswordWordlist if (Line.strip()))
            except Exception:
                self.Cmd.Clear(f"{sd.eBan}{bc.BC} Failed to open Password Wordlist: {bc.RC} {self.Wordlist}\n", True)
        elif self.AttackMode == "bruteforce":
            generator = BruteForceGenerator(**self.BruteForceConfig)
            self.Passwords = generator.generate()
        
    def _get_thread_zip(self):
        # Get or create a ZipFile handle for the current thread
        if not hasattr(self.thread_local, "ZF"):
            try:
                if hasattr(zipfile, 'AESZipFile'):
                    self.thread_local.ZF = zipfile.AESZipFile(self.ZipFile, "r")
                else:
                    self.thread_local.ZF = zipfile.ZipFile(self.ZipFile, "r")
                
                # Cache members too
                self.thread_local.Members = [m for m in self.thread_local.ZF.infolist() if not m.is_dir() and os.path.basename(m.filename)]
                if self.thread_local.Members:
                    self.thread_local.TargetMember = self.thread_local.Members[0]
                else:
                    self.thread_local.TargetMember = None
            except Exception:
                self.thread_local.ZF = None
                self.thread_local.TargetMember = None
        
        return self.thread_local.ZF, self.thread_local.TargetMember

    def _try_password_batch(self, passwords):
        if self.StopEvent: return None
        
        ZF, TargetMember = self._get_thread_zip()
        if not ZF or not TargetMember: return None

        for pwd in passwords:
            if self.StopEvent: return None
            
            # Update progress (approximate)
            self.Tries += 1
            # Print first 100 to show sequence, then every 100 for speed/feedback balance
            if self.Tries < 100 or self.Tries % 100 == 0:
                pwd_str = pwd.decode("utf-8", errors="ignore")
                self.Console.Raw(f"\r[{bc.GC}{self.Tries}{bc.BC}] Trying Password:{bc.GC} {pwd_str}", AppendNewLine=False)

            try:
                ZF.setpassword(pwd)
                with ZF.open(TargetMember) as f:
                    f.read(1)
                
                # If we get here, password is correct!
                # Don't close ZF here as it's thread-local and reused
                return pwd
            except (RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile):
                continue
            except Exception:
                continue
        
        return None

    def CrackPassword(self):
        if not self.Passwords: return
        if not os.path.isfile(self.ZipFile):
            self.Console.Raw(f"{sd.eBan}{bc.BC} Zip File not found: {bc.RC}{self.ZipFile}{bc.BC}")
            return

        os.makedirs(self.ExtractToPath, exist_ok=True)
        
        # Use ThreadPoolExecutor
        max_workers = min(32, (os.cpu_count() or 1) * 4)
        batch_size = 2000 # Optimized batch size

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            while not self.StopEvent:
                # Create batches
                batches = []
                for _ in range(max_workers * 2):
                    batch = list(itertools.islice(self.Passwords, batch_size))
                    if not batch: break
                    
                    # Ensure bytes
                    byte_batch = []
                    for p in batch:
                        if isinstance(p, str): byte_batch.append(p.encode('utf-8'))
                        else: byte_batch.append(p)
                    batches.append(byte_batch)
                
                if not batches: break

                # Submit batches
                futures = {executor.submit(self._try_password_batch, b): b for b in batches}
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        self.FoundPassword = result.decode("utf-8")
                        self.StopEvent = True
                        # Cancel pending
                        for f in futures: f.cancel()
                        break
                
                if self.StopEvent: break

        # If found, extract everything
        if self.FoundPassword:
            try:
                if hasattr(zipfile, 'AESZipFile'):
                    ZF = zipfile.AESZipFile(self.ZipFile, "r")
                else:
                    ZF = zipfile.ZipFile(self.ZipFile, "r")
                
                ZF.setpassword(self.FoundPassword.encode('utf-8'))
                Members = [m for m in ZF.infolist() if not m.is_dir() and os.path.basename(m.filename)]
                
                for Member in Members:
                    FileName = os.path.basename(Member.filename)
                    TargetPath = os.path.join(self.ExtractToPath, FileName)
                    with ZF.open(Member) as Source, open(TargetPath, "wb") as Target:
                        Target.write(Source.read())
                    
                    FileSize = round(os.path.getsize(TargetPath) / 1024, 2)
                    self.ResponseData.append(f"{FileName}:#:{FileSize} KB")
                ZF.close()
            except Exception as e:
                self.Console.Raw(f"\nError extracting: {e}")

    def DisplayResults(self):
        self.Cmd.Clear()
        if self.AttackMode == "dictionary":
            self.Console.Raw(f"Password Wordlist:{bc.GC} {self.Wordlist}", False)
        else:
            self.Console.Raw(f"Attack Mode:{bc.GC} Brute Force", False)
        self.Console.Raw(f"Zip File:{bc.GC} {self.ZipFile}")
        
        if self.FoundPassword:
            self.Console.Success(f"Password Found:{bc.GC} {self.FoundPassword}")
            self.Console.Raw(f"Extracted Contents:")
            FileCount = 1
            for Dat in self.ResponseData:
                Dat = str(Dat)
                File = Dat.split(':#:')[0]
                Size = Dat.split(':#:')[1]
                self.Console.Raw(f"[{bc.GC}File {FileCount}{bc.BC}]:{bc.GC} {File}", False, True)
                self.Console.Raw(f"[{bc.GC}Size{bc.BC}]:{bc.GC} {Size}", True, True)
                FileCount += 1
            self.Console.Success(f"Extraction Complete")
        else:
            self.Console.Raw(f"{sd.eBan}{bc.BC} Password not found.")

    def Rip(self):
        if self.AttackMode == "dictionary":
            self.SetWordlist()
        self.SetZipFile()
        self.SetZipFileDirectory()
        self.SetPasswords()
        self.CrackPassword()
        self.DisplayResults()		

def Initiate():
    try:
        ZipRip().Rip()
    except KeyboardInterrupt:
        quit()
