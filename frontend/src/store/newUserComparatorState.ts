
export const highlightNewUserRow = (rowData: any) => {
    // console.log('row', rowData)
    if(rowData.isNewUser) {
        return {
            'background-color': '#C2E0FF',
            'box-shadow': 'inset 0 0 0 0.063rem #85C2FF'
        }
    }
}