async function SetStatus(teststatus,reason, page) {
  if (teststatus == 'PASS') {
    await page.evaluate(_ => { }, `browserstack_executor: ${JSON.stringify({ action: 'setSessionStatus', arguments: { status: 'passed', reason: 'Passed' } })}`);
  } else {
    await page.evaluate((reason) => { }, `browserstack_executor: ${JSON.stringify({ action: 'setSessionStatus', arguments: { status: 'failed', reason: reason } })}`);
  }
}

async function SetSessionName(testname, page) {
    await page.evaluate((testname) => { }, `browserstack_executor: ${JSON.stringify({ action: 'setSessionName', arguments: { name: testname} })}`);
}

exports.__esModule = true;
exports.SetStatus = SetStatus;
exports.SetSessionName = SetSessionName;
