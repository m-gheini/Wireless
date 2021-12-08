#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/lte-module.h"
#include "ns3/netanim-module.h"
#include <iostream>
#include <fstream>

using namespace std;
using namespace ns3;

#define PI 3.141592653589

ofstream logFile("constantVelocityLog.txt");
// ofstream logFile("constantAccelerationLog.txt");

void NotifyConnectionEstablishedUe (string context, uint64_t imsi, uint16_t cellid, uint16_t rnti) {
    logFile << context << " UE IMSI " << imsi << ": connected to CellId " << cellid << " with RNTI " << rnti << endl;
}

void NotifyHandoverStartUe (string context, uint64_t imsi, uint16_t cellid, uint16_t rnti, uint16_t targetCellId) {
    logFile << context << " UE IMSI " << imsi << ": previously connected to CellId " << cellid << " with RNTI " << rnti
         << ", doing handover to CellId " << targetCellId << endl;
}

void NotifyHandoverEndOkUe (string context, uint64_t imsi, uint16_t cellid, uint16_t rnti) {
    logFile << context << " UE IMSI " << imsi << ": successful handover to CellId " << cellid << " with RNTI " << rnti << endl;
}

void NotifyConnectionEstablishedEnb (string context, uint64_t imsi, uint16_t cellid, uint16_t rnti) {
    logFile << context << " eNB CellId " << cellid << ": successful connection of UE with IMSI " << imsi << " RNTI " << rnti << endl;
}

void NotifyHandoverStartEnb (string context, uint64_t imsi, uint16_t cellid, uint16_t rnti, uint16_t targetCellId) {
    logFile << context << " eNB CellId " << cellid << ": start handover of UE with IMSI " << imsi << " RNTI " << rnti
         << " to CellId " << targetCellId << endl;
}

void NotifyHandoverEndOkEnb (string context, uint64_t imsi, uint16_t cellid, uint16_t rnti) {
    logFile << context << " eNB CellId " << cellid << ": completed handover of UE with IMSI " << imsi << " RNTI " << rnti << endl << endl;
}

int main (int argc, char *argv[]) {
    
    string animFile = "code.xml" ; 
    uint16_t numberOfUes = 10;
    uint16_t numberOfEnbs = 5;
    double distance = 500.0;
    double speed = 100;
    // double acceleration = 100;
    double simTime = (double)(numberOfEnbs + 1) * distance / speed;
    double enbTxPowerDbm = 46.0;

    CommandLine cmd (__FILE__);
    cmd.AddValue ("simTime", "Total duration of the simulation (in seconds)", simTime);
    cmd.AddValue ("speed", "Speed of the UE (default = 100 m/s)", speed);
    cmd.AddValue ("enbTxPowerDbm", "TX power [dBm] used by HeNBs (default = 46.0)", enbTxPowerDbm);
    cmd.Parse (argc, argv);

    Ptr<LteHelper> lteHelper = CreateObject<LteHelper> ();
    Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper> ();
    lteHelper->SetEpcHelper (epcHelper);
    lteHelper->SetSchedulerType ("ns3::RrFfMacScheduler");
    lteHelper->SetHandoverAlgorithmType ("ns3::A2A4RsrqHandoverAlgorithm");
    lteHelper->SetHandoverAlgorithmAttribute ("ServingCellThreshold",UintegerValue (30));
    lteHelper->SetHandoverAlgorithmAttribute ("NeighbourCellOffset",UintegerValue (1));

    NodeContainer ueNodes;
    NodeContainer enbNodes;
    enbNodes.Create (numberOfEnbs);
    ueNodes.Create (numberOfUes);

    Ptr<ListPositionAllocator> enbPositionAlloc = CreateObject<ListPositionAllocator> ();
    for (uint16_t i = 0; i < numberOfEnbs; i++) { 
        Vector enbPosition (distance * (i + 1), distance, 0);
        enbPositionAlloc->Add (enbPosition);
    }
    MobilityHelper enbMobility;
    enbMobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
    enbMobility.SetPositionAllocator (enbPositionAlloc);
    enbMobility.Install (enbNodes);

    Ptr<ListPositionAllocator> uePositionAlloc = CreateObject<ListPositionAllocator> ();
    for (uint16_t j = 0; j < numberOfUes; j++) {  
        double theta = 2*PI*((double)rand() / RAND_MAX);
        double x = (distance/2) * cos(theta);
        double y = (distance/2) * sin(theta);
        Vector uePosition (x + distance, y + distance , 0);
        uePositionAlloc->Add (uePosition);
    }
    MobilityHelper ueMobility;
    ueMobility.SetMobilityModel ("ns3::ConstantVelocityMobilityModel");
    // ueMobility.SetMobilityModel ("ns3::ConstantAccelerationMobilityModel");
    ueMobility.SetPositionAllocator (uePositionAlloc);
    ueMobility.Install (ueNodes);
    for (uint16_t z = 0; z < numberOfUes; z++){
        ueNodes.Get (z)->GetObject<ConstantVelocityMobilityModel> ()->SetVelocity (Vector (speed, 0, 0));
    }
    // for (uint16_t z = 0; z < numberOfUes; z++) {
    //     ueNodes.Get (z)->GetObject<ConstantAccelerationMobilityModel> ()->SetVelocityAndAcceleration (Vector (speed, 0, 0),Vector (acceleration, 0, 0));
    // }

    Config::SetDefault ("ns3::LteEnbPhy::TxPower", DoubleValue (enbTxPowerDbm));
    NetDeviceContainer enbLteDevs = lteHelper->InstallEnbDevice (enbNodes);
    NetDeviceContainer ueLteDevs = lteHelper->InstallUeDevice (ueNodes);

    InternetStackHelper internet;
    internet.Install (ueNodes);
    Ipv4InterfaceContainer ueIpIfaces;
    ueIpIfaces = epcHelper->AssignUeIpv4Address (NetDeviceContainer (ueLteDevs));
    for (uint16_t i = 0; i < numberOfUes; i++) {
        lteHelper->Attach (ueLteDevs.Get (i), enbLteDevs.Get (0));
    }

    lteHelper->AddX2Interface (enbNodes);

    lteHelper->EnablePhyTraces ();
    lteHelper->EnableMacTraces ();
    lteHelper->EnableRlcTraces ();
    lteHelper->EnablePdcpTraces ();

    Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/ConnectionEstablished", MakeCallback (&NotifyConnectionEstablishedEnb));
    Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/ConnectionEstablished", MakeCallback (&NotifyConnectionEstablishedUe));
    Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverStart", MakeCallback (&NotifyHandoverStartEnb));
    Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverStart", MakeCallback (&NotifyHandoverStartUe));
    Config::Connect ("/NodeList/*/DeviceList/*/LteEnbRrc/HandoverEndOk", MakeCallback (&NotifyHandoverEndOkEnb));
    Config::Connect ("/NodeList/*/DeviceList/*/LteUeRrc/HandoverEndOk", MakeCallback (&NotifyHandoverEndOkUe));


    Simulator::Stop (Seconds (simTime));
    AnimationInterface anim (animFile);
    Simulator::Run ();

    Simulator::Destroy ();
    return 0;
}
    
