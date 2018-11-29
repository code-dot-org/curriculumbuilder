let redact;

const VOCABLINK_RE = /^\[v ([^\]]+)\](?:\[([^\]]+)\])?/;
const VOCABLINK = 'vocablink';

/**
 * Plugin that adds support for Curriculum Builder's vocablinks.
 *
 * Note that vocab links are ONLY supported in redaction mode; rendering them
 * out requires CurriculumBuilder database access, so they can only be rendered
 * by Curriculum Builder itself.
 *
 * see https://github.com/mrjoshida/curriculumbuilder/blob/bf74aa5/curriculumBuilder/vocablinks.py
 * @requires restorationRegistration
 */
module.exports = function vocablink() {
  if (this.Parser) {
    const Parser = this.Parser;
    redact = Parser.prototype.options.redact;
    Parser.prototype.inlineTokenizers[VOCABLINK] = tokenizeVocablink;

    Parser.prototype.restorationMethods[VOCABLINK] = function (add, node, content) {
      let value = `[v ${node.vocabword}]`;
      if (content) {
        value += `[${content}]`
      }
      return add({
        type: 'rawtext',
        value 
      });
    }

    // Run it just before `html`
    const methods = Parser.prototype.inlineMethods;
    methods.splice(methods.indexOf('html'), 0, VOCABLINK);
  }
}

tokenizeVocablink.notInLink = true;
tokenizeVocablink.locator = locateVocablink;

function tokenizeVocablink(eat, value, silent) {
  const match = VOCABLINK_RE.exec(value);

  if (match) {
    if (silent) {
      return true;
    }

    const add = eat(match[0]);
    const vocabword = match[1];
    const override = match[2];
    if (redact) {
      return add({
        type: 'redaction',
        redactionType: VOCABLINK,
        vocabword,
        children: [{
          type: 'text',
          value: override || vocabword
        }]
      });
    }

    // In non-redaction mode, eat the vocab link so it is not treated as a
    // different bit of syntax (such as linkReference) but simply output it back
    // to the raw string
    return add({
      type: 'rawtext',
      value: match[0]
    });
  }
}

function locateVocablink(value, fromIndex) {
  return value.indexOf("[v ", fromIndex);
}
