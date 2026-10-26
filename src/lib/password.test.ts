import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hashPassword, checkPassword, digest, token } from './password';
test('parolalar salt ile saklanır, hatalı parola ve bozuk hash reddedilir', async () => {
 const a = await hashPassword('OrnekGuvenliParola123!');
 const b = await hashPassword('OrnekGuvenliParola123!');
 assert.notEqual(a,b);
 assert.equal(await checkPassword('OrnekGuvenliParola123!',a),true);
 assert.equal(await checkPassword('YanlisParola123!',a),false);
 assert.equal(await checkPassword('x','invalid'),false);
 assert.equal(token().length,64);
 assert.notEqual(token(),token());
 assert.equal(digest('test').length,64);
});
