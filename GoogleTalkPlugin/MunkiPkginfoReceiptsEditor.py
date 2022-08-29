#!/usr/local/autopkg/python

from __future__ import absolute_import

from autopkglib import Processor, ProcessorError
from plistlib import load, dump

__all__ = ["MunkiPkginfoReceiptsEditor"]


class MunkiPkginfoReceiptsEditor(Processor):
    '''Modifies the receipts key in a Munki pkginfo.'''

    input_variables = {
        'pkginfo_repo_path': {
            'required': True,
            'description': 'The repo path where the pkginfo was written.',
        },
        'pkg_ids_set_optional_true': {
            'required': True,
            'description': 'Array of package IDs to turn optional for Munki',
        },
    }
    output_variables = {
    }

    description = __doc__

    def main(self):
        if len(self.env['pkginfo_repo_path']) < 1:
            self.output('empty pkginfo path')
            return

        with open(self.env['pkginfo_repo_path'], 'rb') as f:
            pkginfo = load(f)

        receipts_modified = []
        if 'receipts' in pkginfo.keys():
            for i, receipt in enumerate(pkginfo['receipts']):
                # made optional any pkginfos
                if receipt['packageid'] in self.env[
                        'pkg_ids_set_optional_true']:
                    pkginfo['receipts'][i]['optional'] = True
                    self.output(
                        'Setting package ID %s as optional' %
                        receipt['packageid'])
                    receipts_modified.append(receipt['packageid'])
        else:
            raise ProcessorError('pkginfo does not contain receipts key')

        if len(receipts_modified) > 0:
            self.output(
                'Writing pkginfo to %s' %
                self.env['pkginfo_repo_path'])
            with open(self.env['pkginfo_repo_path'], 'wb') as f:
                dump(pkginfo, f)
        else:
            self.output('No receipts modified, not writing pkginfo')


if __name__ == '__main__':
    processor = MunkiPkginfoReceiptsEditor()
    processor.execute_shell()
