import { test } from "node:test";
import assert from "node:assert/strict";
import { unitInput,dateInput,siteInput } from "./property-validation";
test("kayıt alanları ve gerçek takvim tarihi doğrulanır",()=>{
 const unit={number:" 12 ",floor:null,sectionType:"RESIDENTIAL",usageStatus:"UNKNOWN"};
 assert.equal(unitInput.parse(unit).number,"12");
 for(const floor of [-21,201,1.5,NaN]) assert.throws(()=>unitInput.parse({...unit,floor}));
 assert.throws(()=>unitInput.parse({...unit,sectionType:"INVALID"}));
 assert.throws(()=>unitInput.parse({...unit,usageStatus:"INVALID"}));
 assert.throws(()=>dateInput.parse("2026-02-30"));
 assert.equal(dateInput.parse("2026-04-01").toISOString(),"2026-04-01T00:00:00.000Z");
 assert.throws(()=>siteInput.parse({name:" ",address:"",description:""}));
});
