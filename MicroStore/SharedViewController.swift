//
//  SharedViewController.swift
//  MicroStore
//
//  Created by Tomer Volloch on 25/04/2023.
//

import UIKit

class SharedViewController: UIViewController {
    
    @IBOutlet weak var tableView: UITableView!
    
    var dirs: [SharedItem] = []
    var files: [SharedItem] = []
    
    var currPath: String = ""
    
    var isLoading = false
    let activityIndicator = UIActivityIndicatorView(style: .medium)
    
    func scrollViewDidScroll(_ scrollView: UIScrollView) {
        if scrollView.contentOffset.y == -4 && !isLoading{
            isLoading = true
            
            Task {
                let (dirs, files) = await sock.getShared(path: currPath)
                self.dirs = dirs
                self.files = files
                self.tableView.reloadData()
            }
        }
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        currPath = ""
        
        tableView.dataSource = self
        tableView.delegate = self
        
        Task{
            let (dirs, files) = await sock.getShared(path: currPath)
            
            DispatchQueue.main.async {
                self.dirs = dirs
                self.files = files
                self.tableView.reloadData()
            }
        }
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}

    extension SharedViewController : UITableViewDataSource, UITableViewDelegate {
    
    func numberOfSections(in tableView: UITableView) -> Int {
        return 2
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return section == 0 ? dirs.count : files.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell =  tableView.dequeueReusableCell(withIdentifier: "fileCell", for: indexPath)
        if indexPath.section == 0 {
            cell.textLabel?.text = dirs[indexPath.row].name
            cell.detailTextLabel?.text = dirs[indexPath.row].perm
        } else {
            cell.textLabel?.text = files[indexPath.row].name
            cell.detailTextLabel?.text = files[indexPath.row].perm
        }

        return cell
    }
        
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        
        let isDirectory = indexPath.section == 0
        let itemName = isDirectory ? dirs[indexPath.row].name : files[indexPath.row].name
        
        let actionSheet = UIAlertController(title: nil, message: "Choose an action for \(itemName)", preferredStyle: .actionSheet)
        
        let shareAction = UIAlertAction(title: "Share", style: .default) { _ in
            // Call your sock.share function here
            // Example: await sock.share(itemName: itemName, isDirectory: isDirectory)
        }
        
        let changeNameAction = UIAlertAction(title: "Change Name", style: .default) { _ in
            // Call your sock.changename function here
            // Example: await sock.changename(itemName: itemName, isDirectory: isDirectory)
        }
        
        let cancelAction = UIAlertAction(title: "Cancel", style: .cancel, handler: nil)
        
        actionSheet.addAction(shareAction)
        actionSheet.addAction(changeNameAction)
        actionSheet.addAction(cancelAction)
        
        tableView.deselectRow(at: indexPath, animated: true)
        
        self.present(actionSheet, animated: true, completion: nil)
    }
}


struct SharedItem {
    let name: String
    let perm: String
    let uuid: String
    
}
