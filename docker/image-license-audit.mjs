// Inventory evidence only. This does not clear an image for binary distribution.
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
const packages={};
for(const name of ['next','sharp','@img/sharp-libvips-linux-x64','@prisma/client']){
 const root=`node_modules/${name}`;
 if(!existsSync(`${root}/package.json`)){packages[name]={present:false};continue;}
 const p=JSON.parse(readFileSync(`${root}/package.json`,'utf8'));
 packages[name]={present:true,version:p.version,license:p.license??'not in package metadata',noticeFiles:readdirSync(root).filter(n=>/^(license|notice|copying)/i.test(n))};
}
const installed=execFileSync('dpkg-query',['-W','-f=${Package}\t${Version}\n'],{encoding:'utf8'}).trim().split('\n');
console.log(JSON.stringify({binaryDistributionReadiness:'BLOCKED FOR BINARY DISTRIBUTION',scope:'runtime inventory; corresponding-source and notice completeness not proven',nodeVersion:process.version,nodeLicensePresent:existsSync('/usr/local/LICENSE'),basePackageCount:installed.length,baseCopyrightFiles:{libc6:existsSync('/usr/share/doc/libc6/copyright'),openssl:existsSync('/usr/share/doc/openssl/copyright')},packages}));
