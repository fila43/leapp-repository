from leapp import reporting


class NisScanner:
    """
    Check configuration of /etc/yp.conf and /etc/nsswitch.conf. Address of NIS server cannot be
    specified by host name if NIS is used to resolve host names.
    Parameters:
        sources (set) set of labels from nsswitch
        data (dict) list of values for each source
    """

    def scan(self):
        self.scan_nsswitch()
        hostnames = self.hostnames_in_yp_conf()

        if "hosts" in self.data:
            if "nis" in self.data["hosts"] and hostnames:
                self.report_error()
            else:
                self.report_succesful()
        else:
            self.report_succesful()

    def report_error(self):
        reporting.create_report([
            reporting.Title('Unsupported NIS configuration found'),
            reporting.Summary("NIS may be used for domain name resolution only if NIS "\
                            "server is specified by IP. NIS servers specified by "\
                            "host name: {}".format(", ".join(hostnames))),
            reporting.Severity(reporting.Severity.MEDIUM)
        ])

    def report_successful(self):
        reporting.create_report([
            reporting.Title('Checking NIS configuration'),
            reporting.Summary('Check successful'),
            reporting.Severity(reporting.Severity.INFO)
        ])

    def hostnames_in_yp_conf(self):
        """
        Scan /etc/yp.conf, return if file contains domain name
        """

        path = "/etc/yp.conf"
        try:
            with open(path) as f:
                lines = f.readlines()
        except IOError:
            return False

        #remove comments
        lines = list(map(lambda x: x.split("#",1)[0], lines))

        re_server = r"\s*domain\s+\S+\s+server\s+(\S+)\s*"
        re_ypserver = r"\s*ypserver\s+(\S+)\s*"

        # Find server name specified in form: domain NISDOMAIN server HOSTNAME
        mtchs = list(filter(lambda x: x is not None,
                map(lambda x: re.match(re_server, x), lines)))

        # Find server name specified in form: ypserver HOSTNAME
        mtchs.extend(list(filter(lambda x: x is not None,
                map(lambda x: re.match(re_ypserver, x), lines))))

        # Get hostnames from matches
        hostnames = list(map(lambda x: x.group(1), mtchs))

        # Get hostnames that are not IP addresses
        not_ips = list()
        for h in hostnames:
            try:
                ipaddress.ip_address(h)
            except ValueError:
                not_ips.append(h)

        return not_ips


    def scan_nsswitch(self):
        """
        Read the contents of the ``/etc/nsswitch.conf`` file.
        Each non-commented line is split into the service and its sources.  The
        sources (e.g. 'files sss') are stored as is, as a string.
        nsswitch.conf is case insensitive.  This means that both the service and
        its sources are converted to lower case and searches should be done
        using lower case text.
        Attributes:
            data (dict): The service dictionary
            errors (list): Non-blank lines which don't contain a ':'
            sources (set): An unordered set of the sources seen in this file
        Sample content::
            # Example:
            #passwd:    db files nisplus nis
            #shadow:    db files nisplus nis
            #group:     db files nisplus nis
            passwd:     files sss
            shadow:     files sss
            group:      files sss
            #initgroups: files
            #hosts:     db files nisplus nis dns
            hosts:      files dns myhostname
        Examples:
            >>> nss = shared[NSSwitchConf]
            >>> 'passwd' in nss
            True
            >>> 'initgroups' in nss
            False
            >>> nss['passwd']
            'files nss'
            >>> 'files' in nss['hosts']
            True
            >>> nss.errors
            []
            >>> nss.sources
            set(['files', 'dns', 'sss', 'myhostname'])
        """

        path = "/etc/nsswitch.conf"
        try:
            with open(path) as f:
                content = f.read()
        except IOError:
            return False

        self.parse_content(content)


    def get_active_lines(lines, comment_char="#"):
        """
        Returns lines, or parts of lines, from content that are not commented out
        or completely empty.  The resulting lines are all individually stripped.
        This is useful for parsing many config files such as ifcfg.
        Parameters:
            lines (list): List of strings to parse.
            comment_char (str): String indicating that all chars following
                are part of a comment and will be removed from the output.
        Returns:
            list: List of valid lines remaining in the input.
        Examples:
            >>> lines = [
            ... 'First line',
            ... '   ',
            ... '# Comment line',
            ... 'Inline comment # comment',
            ... '          Whitespace          ',
            ... 'Last line']
            >>> get_active_lines(lines)
            ['First line', 'Inline comment', 'Whitespace', 'Last line']
        """
        return list(filter(None, (line.split(comment_char, 1)[0].strip() for line in lines)))


    def parse_content(self, content):
        self.errors = []
        self.data = {}
        self.sources = set()
        for line in get_active_lines(content):
            if ':' not in line:
                self.errors.append(line)
            else:
                service, sources = [s.lower().strip() for s in line.split(':', 1)]
                self.data[service] = sources
                self.sources.update(set(sources.split(None)))


