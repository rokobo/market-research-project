var dag=window.dashAgGridComponentFunctions=window.dashAgGridComponentFunctions||{};
const OPT=e=>React.createElement("option",e,e.label);
dag.DeleteRenderer=function(e){return React.createElement("button",{className:"btn btn-outline-secondary btn-sm delete-button",onClick:function(){e.api.applyTransaction({remove:[e.data]})}},React.createElement("i",{className:"bi bi-trash3-fill"}))};
dag.SelectRenderer=function(e){const{setData:t}=e;return React.createElement(window.dash_bootstrap_components.Select,{value:e.value||"",setProps:function(n){const a=n.value;e.node.setDataValue(e.column.colId,a),t(a)},options:e.options,className:"grid-select"})};
dag.NoRowsOverlay=function(){return React.createElement("div",{},"")};
