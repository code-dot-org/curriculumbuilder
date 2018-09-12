let redact;

const TIPLINK_RE = /^([\w-]+)!!! ?([\w-]+)?/
const TIPLINK_LOCATOR_RE = /[\w-]+!!!/;

/**
 * @requires restorationRegistration
 */
module.exports = function mention() {
  if (this.Parser) {
    const Parser = this.Parser;
    const tokenizers = Parser.prototype.inlineTokenizers;
    const methods = Parser.prototype.inlineMethods;
    const restorationMethods = Parser.prototype.restorationMethods;

    restorationMethods.tiplink = function (add, node) {
      return add({
        type: 'text',
        value: `${node.tipType}!!! ${node.tipLink}`
      });
    }

    redact = Parser.prototype.options.redact;

    /* Add an inline tokenizer (defined in the following example). */
    tokenizers.tiplink = tokenizeTiplink;

    /* Run it just before `text`. */
    methods.splice(methods.indexOf('text'), 0, 'tiplink');
  }
}

tokenizeTiplink.notInLink = true;
tokenizeTiplink.locator = locateTiplink;

function createTiplink(add, tipType, tipLink) {
  const element = {
    type: 'paragraph',
    children: [],
    data: {
      hProperties: {
        className: `tiplink tiplink-${tipType}`,
      },
    },
  }


  let icon;
  if (tipType == 'tip') {
    icon = "lightbulb-o";
  } else if (tipType == 'discussion') {
    icon = "comments";
  } else if (tipType == 'content') {
    icon = "mortar-board";
  } else {
    icon = "warning";
  }

  const child = add({
    type: 'link',
    url: `#${tipType}_${tipLink}`,
    children: []
  }, element);

  add({
    type: 'emphasis',
    children: [],
    data: {
      hName: 'i',
      hProperties: {
        className: `fa fa-${icon}`
      },
    },
  }, child)

  return add(element);
}

function tokenizeTiplink(eat, value, silent) {
  const match = TIPLINK_RE.exec(value);

  if (match) {
    if (silent) {
      return true;
    }

    const add = eat(match[0]);
    const tipType = match[1];
    const tipLink = match[2];

    if (redact) {
      return add({
        type: 'redaction',
        redactionType: 'tiplink',
        tipType,
        tipLink
      });
    }

    return createTiplink(add, tipType, tipLink);
  }
}

function locateTiplink(value, fromIndex) {
  const match = TIPLINK_LOCATOR_RE.exec(value);
  if (match && match.index >= fromIndex) {
    return match.index;
  }
}
