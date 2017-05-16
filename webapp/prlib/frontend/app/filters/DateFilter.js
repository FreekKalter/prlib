import React from 'react';
import { shapes } from 'react-data-grid';
const { ExcelColumn } = shapes;

const RuleType = {
  Number: 1,
  Range: 2,
  GreaterThen: 3,
  LessThen: 4
};

class NumericFilter extends React.Component {
  constructor(props) {
    super(props);
    this.handleChange = this.handleChange.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
    this.getRules = this.getRules.bind(this);
  }

  filterValues(row, columnFilter, columnKey) {
    if (columnFilter.filterTerm == null) {
      return true;
    }
    let result = false;
    // implement default filter logic
    let value = parseInt(row[columnKey], 10);
    for (let ruleKey in columnFilter.filterTerm) {
      if (!columnFilter.filterTerm.hasOwnProperty(ruleKey)) {
        continue;
      }

      let rule = columnFilter.filterTerm[ruleKey];

      switch (rule.type) {
      case RuleType.Number:
        if (rule.value === value) {
          result = true;
        }
        break;
      case RuleType.GreaterThen:
        if (rule.value <= value) {
          result = true;
        }
        break;
      case RuleType.LessThen:
        if (rule.value >= value) {
          result = true;
        }
        break;
      case RuleType.Range:
        if (rule.begin <= value && rule.end >= value ) {
          result = true;
        }
        break;
      default:
        // do nothing
        break;
      }
    }
    return result;
  }

  getRules(value) {
    let rules = [];
    if (value === '') {
      return rules;
    }
    // check comma
    let list = value.split(',');
    if (list.length > 0) {
      // handle each value with comma
      for (let key in list) {
        if (!list.hasOwnProperty(key)) {
          continue;
        }

        let obj = list[key];
        try{
            if (obj.indexOf('-') > 0) { // handle dash
              let begin = this.parseDate(obj.split('-')[0].trim());
              let end = this.parseDate(obj.split('-')[1].trim());
              rules.push({ type: RuleType.Range, begin: begin, end: end });
            } else if (obj.indexOf(':') > -1) {
                if(obj.split(':')[0] == 'after'){ // handle greater then
                  let begin = this.parseDate(obj.split(':')[1].trim())
                  rules.push({ type: RuleType.GreaterThen, value: begin });
                } else if(obj.split(':')[0] == 'before'){ // handle less then
                  let end = this.parseDate(obj.split(':')[1].trim())
                  rules.push({ type: RuleType.LessThen, value: end });
                }
            }
        }catch(e){}
      }
    }
    return rules;
  }

  parseDate(value){
      var s = value.split('/');
      if(s[2].length == 2){
          s[2] = '20' + s[2];
      }
      var seconds = Date.UTC(s[2], s[1], s[0])/1000;
      return(seconds);
  }

  handleKeyPress(e) { // Validate the input
    //let regex = '>|<|-|,|([0-9])';
    //let result = RegExp(regex).test(e.key);
    //if (result === false) {
      //e.preventDefault();
    //}
  }

  handleChange(e) {
    let value = e.target.value;
    let filters = this.getRules(value);
    this.props.onChange({filterTerm: (filters.length > 0 ? filters : null), column: this.props.column, rawValue: value, filterValues: this.filterValues });
  }

  render() {
    let inputKey = 'header-filter-' + this.props.column.key;
    let columnStyle = {
      float: 'left',
      marginRight: 5,
      maxWidth: '80%'
    };
    let badgeStyle = {
      cursor: 'help'
    };

    return (
      <div>
        <div style={columnStyle}>
          <input key={inputKey} type="text" placeholder="after: 13/1/2016" className="form-control input-sm" onChange={this.handleChange} onKeyPress={this.handleKeyPress}/>
        </div>
      </div>
    );
  }
}

NumericFilter.propTypes = {
  onChange: React.PropTypes.func.isRequired,
  column: React.PropTypes.shape(ExcelColumn)
};
module.exports = NumericFilter;
