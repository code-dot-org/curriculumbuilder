let redact;

const RESOURCELINK_RE = /^\[r ([^\]]+)\]/;
const RESOURCELINK = 'resourcelink';

/**
 * Plugin that adds support for Curriculum Builder's resourcelinks.
 *
 * Note that resource links are ONLY supported in redaction mode; rendering them
 * out requires CurriculumBuilder database access, so they can only be rendered
 * by Curriculum Builder itself.
 *
 * see https://github.com/mrjoshida/curriculumbuilder/blob/bf74aa5/curriculumBuilder/resourcelinks.py
 * @requires restorationRegistration
 */
module.exports = function resourcelink() {
  if (this.Parser) {
    const Parser = this.Parser;
    redact = Parser.prototype.options.redact;
    Parser.prototype.inlineTokenizers[RESOURCELINK] = tokenizeResourcelink;

    Parser.prototype.restorationMethods[RESOURCELINK] = function (add, node) {
      return add({
        type: 'rawtext',
        value: `[r ${node.slug}]`
      });
    }

    // Run it just before `html`
    const methods = Parser.prototype.inlineMethods;
    methods.splice(methods.indexOf('html'), 0, RESOURCELINK);
  }
}

tokenizeResourcelink.notInLink = true;
tokenizeResourcelink.locator = locateResourcelink;

function tokenizeResourcelink(eat, value, silent) {
  const match = RESOURCELINK_RE.exec(value);

  // Resource links are ONLY supported in redaction mode
  if (match && redact) {
    if (silent) {
      return true;
    }

    const slug = match[1];
    return eat(match[0])({
      type: 'redaction',
      redactionType: RESOURCELINK,
      slug,
      children: [{
        type: 'text',
        value: slug
      }]
    });
  }
}

function locateResourcelink(value, fromIndex) {
  return value.indexOf("[r ", fromIndex);
}
